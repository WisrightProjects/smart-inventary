"""Compares expected box contents against AI-detected product counts.

Implements the six verification outcomes from the spec:
  VERIFIED, WRONG_PRODUCT, MISSING_PRODUCT, EXTRA_PRODUCT,
  UNEXPECTED_PRODUCT, MIXED_PRODUCTS
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    WRONG_PRODUCT = "WRONG_PRODUCT"
    MISSING_PRODUCT = "MISSING_PRODUCT"
    EXTRA_PRODUCT = "EXTRA_PRODUCT"
    UNEXPECTED_PRODUCT = "UNEXPECTED_PRODUCT"
    MIXED_PRODUCTS = "MIXED_PRODUCTS"


@dataclass
class VerificationResult:
    status: VerificationStatus
    expected: dict[str, int]
    detected: dict[str, int]
    details: str

    def to_dict(self) -> dict:
        return {
            "status": self.status.value,
            "expected": self.expected,
            "detected": self.detected,
            "details": self.details,
        }


def verify(expected: dict[str, int], detected: dict[str, int]) -> VerificationResult:
    """Compares expected box contents (from a scanned Box ID) with detected
    product counts (from RT-DETR) and returns a single verification status.

    expected: e.g. {"Pencil": 10}
    detected: e.g. {"Pencil": 10} / {"Notebook": 10} / {"Pencil": 5, "Book": 2}
    """
    expected_names = set(expected)
    detected_names = set(detected)

    # Case 2: every detected item is a product not present in expected at all.
    if detected_names and detected_names.isdisjoint(expected_names):
        return VerificationResult(
            VerificationStatus.WRONG_PRODUCT,
            expected,
            detected,
            "Detected product(s) do not match any expected product for this box.",
        )

    extra_names = detected_names - expected_names
    missing_or_short: list[str] = []
    extra_qty_names: list[str] = []

    for name, expected_qty in expected.items():
        detected_qty = detected.get(name, 0)
        if detected_qty < expected_qty:
            missing_or_short.append(name)
        elif detected_qty > expected_qty:
            extra_qty_names.append(name)

    has_unexpected_extra_product = bool(extra_names)
    has_short = bool(missing_or_short)
    has_over = bool(extra_qty_names)

    # Case 6: some expected products short AND unexpected extra products present.
    if has_short and has_unexpected_extra_product:
        return VerificationResult(
            VerificationStatus.MIXED_PRODUCTS,
            expected,
            detected,
            "Some expected products are missing while unexpected products are present.",
        )

    # Case 5: expected quantities fully met, but an extra unexpected product also present.
    if not has_short and not has_over and has_unexpected_extra_product:
        return VerificationResult(
            VerificationStatus.UNEXPECTED_PRODUCT,
            expected,
            detected,
            f"Expected products fully matched, but unexpected product(s) also found: {', '.join(sorted(extra_names))}.",
        )

    # Case 3: an expected product is short, no unexpected extras.
    if has_short:
        return VerificationResult(
            VerificationStatus.MISSING_PRODUCT,
            expected,
            detected,
            f"Missing quantity for: {', '.join(sorted(missing_or_short))}.",
        )

    # Case 4: an expected product has more units than expected, no unexpected extras.
    if has_over:
        return VerificationResult(
            VerificationStatus.EXTRA_PRODUCT,
            expected,
            detected,
            f"Extra quantity detected for: {', '.join(sorted(extra_qty_names))}.",
        )

    # Case 1: exact match.
    return VerificationResult(
        VerificationStatus.VERIFIED,
        expected,
        detected,
        "Detected products and quantities match expected inventory exactly.",
    )
