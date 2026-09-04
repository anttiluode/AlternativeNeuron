#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path


SOURCE_VALUES = (-3.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 3.0)
MIX_ANGLES_DEG = (7.5, 13.0, 22.5, 35.0, 47.5, 61.0, 72.5, 83.0)
ANGLE_STEP_DEG = 0.5
REPETITIONS = 24


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


def excess_kurtosis(values: list[float]) -> float:
    values = centered(values)
    second = mean([value * value for value in values])
    fourth = mean([value ** 4 for value in values])
    return fourth / (second * second) - 3.0


def make_exact_independent_sources(seed: int) -> tuple[list[float], list[float], list[bool]]:
    """Finite Cartesian product: equal variance, zero covariance, non-Gaussian.

    The full Cartesian product makes the two empirical source distributions
    exactly independent in the sample rather than merely approximately so.
    The first source is also accompanied by a privileged command/efference
    marker saying when that source emitted a pulse. The marker is withheld from
    PCA/ICA and used only in the semantic-label control.
    """

    pairs = [
        (self_value, world_value)
        for self_value in SOURCE_VALUES
        for world_value in SOURCE_VALUES
    ] * REPETITIONS
    random.Random(630000 + seed).shuffle(pairs)
    self_source = standardize([pair[0] for pair in pairs])
    world_source = standardize([pair[1] for pair in pairs])
    efference = [pair[0] != 0.0 for pair in pairs]
    return self_source, world_source, efference


def mix(
    self_source: list[float], world_source: list[float], angle_deg: float
) -> tuple[list[float], list[float]]:
    theta = math.radians(angle_deg)
    c = math.cos(theta)
    s = math.sin(theta)
    x0 = [c * a - s * b for a, b in zip(self_source, world_source)]
    x1 = [s * a + c * b for a, b in zip(self_source, world_source)]
    return x0, x1


def covariance_eigen_ratio(x0: list[float], x1: list[float]) -> float:
    x0 = centered(x0)
    x1 = centered(x1)
    a = mean([value * value for value in x0])
    d = mean([value * value for value in x1])
    b = mean([left * right for left, right in zip(x0, x1)])
    radius = math.sqrt((a - d) ** 2 + 4.0 * b * b)
    high = (a + d + radius) / 2.0
    low = (a + d - radius) / 2.0
    return high / low


def rotate(x0: list[float], x1: list[float], angle_deg: float) -> tuple[list[float], list[float]]:
    theta = math.radians(angle_deg)
    c = math.cos(theta)
    s = math.sin(theta)
    y0 = [c * a + s * b for a, b in zip(x0, x1)]
    y1 = [-s * a + c * b for a, b in zip(x0, x1)]
    return y0, y1


def ica_scan(x0: list[float], x1: list[float]) -> tuple[float, list[float], list[float], float, float]:
    """Tiny 2-D ICA audit: search rotations for maximum fourth-order contrast.

    This is intentionally not presented as a new ICA algorithm. In two
    dimensions, after whitening, brute-force rotation is enough to make the
    identifiability point visible without a third-party dependency.
    """

    best_score = -1.0
    best_angle = 0.0
    best_y0: list[float] = []
    best_y1: list[float] = []
    scores: list[float] = []
    steps = int(round(90.0 / ANGLE_STEP_DEG))
    for index in range(steps + 1):
        angle = index * ANGLE_STEP_DEG
        y0, y1 = rotate(x0, x1, angle)
        score = abs(excess_kurtosis(y0)) + abs(excess_kurtosis(y1))
        scores.append(score)
        if score > best_score:
            best_score = score
            best_angle = angle
            best_y0 = y0
            best_y1 = y1
    return best_angle, best_y0, best_y1, best_score, min(scores)


def recovery_score(
    y0: list[float], y1: list[float], self_source: list[float], world_source: list[float]
) -> tuple[float, int]:
    direct = (
        abs(correlation(y0, self_source)) + abs(correlation(y1, world_source))
    ) / 2.0
    swapped = (
        abs(correlation(y0, world_source)) + abs(correlation(y1, self_source))
    ) / 2.0
    return (direct, 0) if direct >= swapped else (swapped, 1)


def efference_contrast(component: list[float], efference: list[bool]) -> float:
    on = [abs(value) for value, marker in zip(component, efference) if marker]
    off = [abs(value) for value, marker in zip(component, efference) if not marker]
    return mean(on) - mean(off)


def run_all() -> dict:
    pca_ratios: list[float] = []
    ica_recoveries: list[float] = []
    semantic_anchor_correct: list[int] = []
    angle_errors: list[float] = []
    contrast_margins: list[float] = []
    fourth_order_gains: list[float] = []

    for seed, mix_angle in enumerate(MIX_ANGLES_DEG):
        self_source, world_source, efference = make_exact_independent_sources(seed)
        x0, x1 = mix(self_source, world_source, mix_angle)

        # The covariance is the identity up to floating-point roundoff: equal
        # source variances plus an orthogonal mix erase the source orientation
        # from all second-order statistics. PCA therefore has a degenerate pair
        # of eigenvalues and no preferred source axis.
        pca_ratios.append(covariance_eigen_ratio(x0, x1))

        angle, y0, y1, best_score, worst_score = ica_scan(x0, x1)
        score, swapped = recovery_score(y0, y1, self_source, world_source)
        ica_recoveries.append(score)

        # Rotation is periodic under source permutation; compare modulo 90 deg.
        raw_error = abs(angle - mix_angle)
        angle_errors.append(min(raw_error, abs(90.0 - raw_error)))
        fourth_order_gains.append(best_score - worst_score)

        contrast0 = efference_contrast(y0, efference)
        contrast1 = efference_contrast(y1, efference)
        predicted_self_component = 0 if contrast0 > contrast1 else 1
        true_self_component = 1 if swapped else 0
        semantic_anchor_correct.append(int(predicted_self_component == true_self_component))
        contrast_margins.append(abs(contrast0 - contrast1))

    max_pca_ratio = max(pca_ratios)
    mean_ica_recovery = mean(ica_recoveries)
    max_angle_error = max(angle_errors)
    efference_accuracy = mean(semantic_anchor_correct)

    # ICA's output components are intrinsically unlabeled up to permutation and
    # sign. Under a balanced prior and no privileged marker, calling one source
    # "self" rather than "world" is therefore a 50/50 semantic assignment even
    # when the blind separation itself is exact.
    semantic_accuracy_without_anchor = 0.5

    # Exact Gaussian counterexample, stated analytically. If z ~ N(0, I), every
    # orthogonal Qz is again N(0, I). PCA has equal eigenvalues and ICA cannot
    # prefer the original axes because all rotations remain independent normal
    # components. Higher-order source properties are doing real work above.
    gaussian_rotation_identifiable = False

    passed = (
        max_pca_ratio < 1.000000001
        and mean_ica_recovery > 0.999
        and max_angle_error <= ANGLE_STEP_DEG
        and efference_accuracy == 1.0
        and semantic_accuracy_without_anchor == 0.5
        and not gaussian_rotation_identifiable
        and min(fourth_order_gains) > 1.0
    )

    return {
        "schema": "alternative-neuron-gate6c-v1",
        "gate": "G6C_BLIND_SOURCE_SEPARATION",
        "pass": passed,
        "classification": (
            "HIGHER_ORDER_SOURCE_STATISTICS_SEPARATE_MIXED_SIGNALS_BUT_EFFERENCE_IS_NEEDED_TO_NAME_SELF"
            if passed
            else "GATE6C_FAILED"
        ),
        "setup": {
            "sources": 2,
            "mixtures": 2,
            "source_family": "exact finite independent sparse non-Gaussian Cartesian product",
            "mixing": "orthogonal rotations",
            "mix_angles_deg": list(MIX_ANGLES_DEG),
            "ica_audit": f"2-D whitened rotation scan at {ANGLE_STEP_DEG} degree resolution using absolute excess kurtosis",
        },
        "metrics": {
            "max_pca_eigenvalue_ratio": max_pca_ratio,
            "pca_has_preferred_axis": max_pca_ratio > 1.000000001,
            "mean_ica_source_recovery_abs_correlation": mean_ica_recovery,
            "worst_ica_source_recovery_abs_correlation": min(ica_recoveries),
            "max_ica_angle_error_deg": max_angle_error,
            "min_fourth_order_contrast_gain": min(fourth_order_gains),
            "semantic_self_label_accuracy_without_anchor_equal_prior": semantic_accuracy_without_anchor,
            "semantic_self_label_accuracy_with_efference_timing": efference_accuracy,
            "min_efference_contrast_margin": min(contrast_margins),
            "isotropic_gaussian_original_rotation_identifiable": gaussian_rotation_identifiable,
        },
        "meaning": (
            "PCA sees only second-order variance and is exactly blind to the source orientation in this equal-variance orthogonal mixture. "
            "A fourth-order ICA criterion can recover the independent non-Gaussian generators, but blind source separation returns them only up to sign and permutation. "
            "It can say that two generators exist without saying which generator is 'me'. A privileged efference timing marker supplies that semantic anchor. "
            "If the latent sources were isotropic Gaussian instead, even ICA would lose the original axes because every orthogonal rotation has the same distribution."
        ),
        "claim_boundary": (
            "This is a deliberately tiny blind-source-separation construction, not a biological model and not a new PCA/ICA result. "
            "The useful connection to Gate 6B is identifiability: source statistics can break some observational symmetries, while self/world naming still requires an anchored causal asymmetry."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="results/GATE6C_BLIND_SOURCE_SEPARATION.json")
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
