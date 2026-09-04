#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path


MIX_ANGLES_DEG = (7.5, 13.0, 22.5, 35.0, 47.5, 61.0, 72.5, 83.0)
TRUE_LAG = 5
MAX_LAG = 8
N = 4096
ANGLE_STEP_DEG = 0.5
FLY_SCALE = 6.0


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def centered(values: list[float]) -> list[float]:
    m = mean(values)
    return [value - m for value in values]


def standardize(values: list[float]) -> list[float]:
    values = centered(values)
    variance = mean([value * value for value in values])
    scale = math.sqrt(variance)
    return [value / scale for value in values]


def correlation(a: list[float], b: list[float]) -> float:
    aa = centered(a)
    bb = centered(b)
    numerator = sum(x * y for x, y in zip(aa, bb))
    denominator = math.sqrt(sum(x * x for x in aa) * sum(y * y for y in bb))
    return numerator / denominator


def signed_lag_correlation(command: list[float], signal: list[float], lag: int) -> float:
    """corr(command[t], signal[t+lag]); positive lag means signal follows command."""

    if lag > 0:
        return correlation(command[:-lag], signal[lag:])
    if lag < 0:
        shift = -lag
        return correlation(command[shift:], signal[:-shift])
    return correlation(command, signal)


def excess_kurtosis(values: list[float]) -> float:
    values = centered(values)
    second = mean([value * value for value in values])
    fourth = mean([value ** 4 for value in values])
    return fourth / (second * second) - 3.0


def rotate(x0: list[float], x1: list[float], angle_deg: float) -> tuple[list[float], list[float]]:
    theta = math.radians(angle_deg)
    c = math.cos(theta)
    s = math.sin(theta)
    y0 = [c * a + s * b for a, b in zip(x0, x1)]
    y1 = [-s * a + c * b for a, b in zip(x0, x1)]
    return y0, y1


def mix(self_source: list[float], partner_source: list[float], angle_deg: float) -> tuple[list[float], list[float]]:
    theta = math.radians(angle_deg)
    c = math.cos(theta)
    s = math.sin(theta)
    x0 = [c * a - s * b for a, b in zip(self_source, partner_source)]
    x1 = [s * a + c * b for a, b in zip(self_source, partner_source)]
    return x0, x1


def ica_scan(x0: list[float], x1: list[float]) -> tuple[float, list[float], list[float], float]:
    """Tiny static 2-D ICA audit; copied in spirit from Gate 6C."""

    best_score = -1.0
    best_angle = 0.0
    best_y0: list[float] = []
    best_y1: list[float] = []
    steps = int(round(90.0 / ANGLE_STEP_DEG))
    for index in range(steps + 1):
        angle = index * ANGLE_STEP_DEG
        y0, y1 = rotate(x0, x1, angle)
        score = abs(excess_kurtosis(y0)) + abs(excess_kurtosis(y1))
        if score > best_score:
            best_score = score
            best_angle = angle
            best_y0 = y0
            best_y1 = y1
    return best_angle, best_y0, best_y1, best_score


def source_recovery(
    y0: list[float], y1: list[float], self_source: list[float], partner_source: list[float]
) -> tuple[float, int]:
    direct = (
        abs(correlation(y0, self_source)) + abs(correlation(y1, partner_source))
    ) / 2.0
    swapped = (
        abs(correlation(y0, partner_source)) + abs(correlation(y1, self_source))
    ) / 2.0
    return (direct, 0) if direct >= swapped else (swapped, 1)


def sparse_value(rng: random.Random, negative: float, positive: float) -> float:
    draw = rng.random()
    if draw < negative:
        return -1.0
    if draw < positive:
        return 1.0
    return 0.0


def make_sources(seed: int) -> tuple[list[float], list[float], list[float]]:
    """Command, delayed responder, and a loud unrelated distractor.

    The responder is not a mere copy: it combines a delayed command contribution
    with its own independent innovation stream. At the same instant the command
    and responder are almost uncorrelated; their relation lives primarily in
    temporal direction.
    """

    rng = random.Random(730000 + seed)
    command = [sparse_value(rng, 0.11, 0.22) for _ in range(N)]
    innovation = [sparse_value(rng, 0.09, 0.18) for _ in range(N)]
    fly = [sparse_value(rng, 0.30, 0.60) for _ in range(N)]

    partner: list[float] = []
    for timestep in range(N):
        delayed = command[timestep - TRUE_LAG] if timestep >= TRUE_LAG else 0.0
        partner.append(0.80 * delayed + 0.60 * innovation[timestep])

    return standardize(command), standardize(partner), standardize(fly)


def variance(values: list[float]) -> float:
    values = centered(values)
    return mean([value * value for value in values])


def lag_peak(command: list[float], signal: list[float]) -> tuple[int, float]:
    curve = {
        lag: abs(signed_lag_correlation(command, signal, lag))
        for lag in range(-MAX_LAG, MAX_LAG + 1)
    }
    lag = max(curve, key=curve.get)
    return lag, curve[lag]


def positive_lag_peak_raw(command: list[float], signals: tuple[list[float], ...]) -> tuple[int, float]:
    best_lag = 1
    best_value = -1.0
    for signal in signals:
        for lag in range(1, MAX_LAG + 1):
            value = abs(signed_lag_correlation(command, signal, lag))
            if value > best_value:
                best_value = value
                best_lag = lag
    return best_lag, best_value


def shuffled_peak(command: list[float], partner_component: list[float], seed: int) -> float:
    shuffled = command.copy()
    random.Random(740000 + seed).shuffle(shuffled)
    return max(
        abs(signed_lag_correlation(shuffled, partner_component, lag))
        for lag in range(-MAX_LAG, MAX_LAG + 1)
    )


def run_all() -> dict:
    recoveries: list[float] = []
    self_labels: list[int] = []
    partner_lags: list[int] = []
    partner_peaks: list[float] = []
    reverse_lags: list[int] = []
    shuffled_peaks: list[float] = []
    static_reverse_score_error: list[float] = []
    raw_lags: list[int] = []
    raw_peaks: list[float] = []
    fly_is_top_variance: list[int] = []
    contemporaneous_source_corr: list[float] = []

    for seed, mix_angle in enumerate(MIX_ANGLES_DEG):
        command, partner, fly = make_sources(seed)
        x0, x1 = mix(command, partner, mix_angle)
        x2 = [FLY_SCALE * value for value in fly]

        variances = [variance(x0), variance(x1), variance(x2)]
        fly_is_top_variance.append(int(max(range(3), key=lambda i: variances[i]) == 2))
        contemporaneous_source_corr.append(abs(correlation(command, partner)))

        _, y0, y1, static_score = ica_scan(x0, x1)
        recovery, swapped = source_recovery(y0, y1, command, partner)
        recoveries.append(recovery)

        components = [y0, y1]
        true_self_component = 1 if swapped else 0
        predicted_self_component = max(
            range(2),
            key=lambda index: abs(signed_lag_correlation(command, components[index], 0)),
        )
        self_labels.append(int(predicted_self_component == true_self_component))

        partner_component = components[1 - predicted_self_component]
        lag, peak = lag_peak(command, partner_component)
        partner_lags.append(lag)
        partner_peaks.append(peak)

        reversed_x0 = list(reversed(x0))
        reversed_x1 = list(reversed(x1))
        _, reversed_y0, reversed_y1, reversed_static_score = ica_scan(reversed_x0, reversed_x1)
        static_reverse_score_error.append(abs(static_score - reversed_static_score))
        reversed_command = list(reversed(command))
        reversed_components = [reversed_y0, reversed_y1]
        reversed_self_component = max(
            range(2),
            key=lambda index: abs(
                signed_lag_correlation(reversed_command, reversed_components[index], 0)
            ),
        )
        reversed_partner_component = reversed_components[1 - reversed_self_component]
        reverse_lag, _ = lag_peak(reversed_command, reversed_partner_component)
        reverse_lags.append(reverse_lag)

        shuffled_peaks.append(shuffled_peak(command, partner_component, seed))

        raw_lag, raw_peak = positive_lag_peak_raw(command, (x0, x1, x2))
        raw_lags.append(raw_lag)
        raw_peaks.append(raw_peak)

    mean_recovery = mean(recoveries)
    mean_true_peak = mean(partner_peaks)
    mean_shuffled_peak = mean(shuffled_peaks)
    raw_lag_accuracy = mean([int(lag == TRUE_LAG) for lag in raw_lags])
    partner_lag_accuracy = mean([int(lag == TRUE_LAG) for lag in partner_lags])
    reverse_lag_accuracy = mean([int(lag == -TRUE_LAG) for lag in reverse_lags])
    self_label_accuracy = mean(self_labels)
    fly_top_variance_fraction = mean(fly_is_top_variance)

    # Static ICA can recover two source axes, but sign/permutation ambiguity does
    # not name one axis as command-originating and the other as responder. Under
    # an equal prior, semantic assignment without an efference/timing anchor is
    # still 50/50 even when source recovery itself is excellent.
    static_semantic_accuracy_without_anchor = 0.5

    passed = (
        mean_recovery > 0.995
        and self_label_accuracy == 1.0
        and partner_lag_accuracy == 1.0
        and reverse_lag_accuracy == 1.0
        and max(static_reverse_score_error) < 1e-10
        and mean_true_peak > 0.75
        and mean_true_peak > mean_shuffled_peak * 8.0
        and fly_top_variance_fraction == 1.0
        and raw_lag_accuracy == 1.0
        and max(contemporaneous_source_corr) < 0.05
    )

    return {
        "schema": "alternative-neuron-gate7b-v1",
        "gate": "G7B_TEMPORAL_CAUSAL_SEPARATION",
        "pass": passed,
        "classification": (
            "STATIC_SOURCE_SEPARATION_RECOVERS_GENERATORS_BUT_DIRECTED_EFFERENCE_TIMING_SUPPLIES_CAUSAL_ADDRESS"
            if passed
            else "GATE7B_FAILED"
        ),
        "setup": {
            "samples": N,
            "true_partner_delay": TRUE_LAG,
            "max_scanned_lag": MAX_LAG,
            "mix_angles_deg": list(MIX_ANGLES_DEG),
            "fly_scale": FLY_SCALE,
            "partner_law": "partner[t] = 0.80*command[t-5] + 0.60*independent_innovation[t]",
            "observations": "two orthogonal command/partner mixtures plus one loud unrelated fly channel",
        },
        "metrics": {
            "mean_static_ica_source_recovery_abs_correlation": mean_recovery,
            "worst_static_ica_source_recovery_abs_correlation": min(recoveries),
            "max_abs_contemporaneous_command_partner_correlation": max(contemporaneous_source_corr),
            "variance_selector_picks_fly_fraction": fly_top_variance_fraction,
            "semantic_command_label_accuracy_without_anchor_equal_prior": static_semantic_accuracy_without_anchor,
            "semantic_command_label_accuracy_with_efference_zero_lag": self_label_accuracy,
            "partner_delay_recovery_accuracy": partner_lag_accuracy,
            "reverse_time_recovers_negative_delay_accuracy": reverse_lag_accuracy,
            "max_static_ica_contrast_change_under_time_reversal": max(static_reverse_score_error),
            "mean_true_partner_lag_correlation": mean_true_peak,
            "mean_shuffled_command_peak_correlation": mean_shuffled_peak,
            "true_over_shuffled_peak_ratio": mean_true_peak / mean_shuffled_peak,
            "raw_lagged_correlation_delay_accuracy": raw_lag_accuracy,
            "mean_raw_lagged_correlation_peak": mean(raw_peaks),
        },
        "meaning": (
            "Static ICA can recover the two non-Gaussian generators, while a variance/PCA-like channel selector is captured by the loud fly. "
            "But static separation alone does not say which recovered component is command-originating or which way the interaction runs. "
            "An efference copy anchors the zero-lag command component; the other component then carries a +5-step response peak. "
            "Reversing time leaves all static ICA evidence unchanged but flips the recovered relation to -5, and shuffling command timing destroys the peak. "
            "A simple raw lagged-correlation attacker also recovers the delay perfectly here, so the gate does not claim that sophisticated source separation is required merely to detect coupling. "
            "The extra object supplied by separation is a reusable source identity plus a directed causal address."
        ),
        "claim_boundary": (
            "Synthetic linear mixtures and a hand-built delayed responder only. This is not a biological attractor model, a new ICA method, or proof that temporal precedence alone establishes causation. "
            "The issued-command/efference record is privileged information and is exactly the asymmetry Gate 6B said was required. "
            "The raw-lag attacker succeeding is an explicit negative: for this simple setting, delay detection itself is easy."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="results/GATE7B_TEMPORAL_CAUSAL_SEPARATION.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    result = run_all()
    text = json.dumps(result, indent=2, sort_keys=True)
    print(text)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text + "\n", encoding="utf-8")
    return 1 if args.check and not result["pass"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
