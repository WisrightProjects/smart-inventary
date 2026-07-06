"""Unit tests for the verification engine's six outcome cases."""
from backend.verification.verifier import VerificationStatus, verify


def test_verified_exact_match():
    result = verify({"Pencil": 10}, {"Pencil": 10})
    assert result.status == VerificationStatus.VERIFIED


def test_wrong_product():
    result = verify({"Pencil": 10}, {"Notebook": 10})
    assert result.status == VerificationStatus.WRONG_PRODUCT


def test_missing_product():
    result = verify({"Notebook": 5}, {"Notebook": 4})
    assert result.status == VerificationStatus.MISSING_PRODUCT


def test_extra_product():
    result = verify({"Notebook": 5}, {"Notebook": 6})
    assert result.status == VerificationStatus.EXTRA_PRODUCT


def test_unexpected_product():
    result = verify({"Notebook": 5}, {"Notebook": 5, "Book": 1})
    assert result.status == VerificationStatus.UNEXPECTED_PRODUCT


def test_mixed_products():
    result = verify({"Notebook": 5}, {"Notebook": 3, "Book": 2})
    assert result.status == VerificationStatus.MIXED_PRODUCTS


def test_empty_detection_is_missing():
    result = verify({"Pencil": 10}, {})
    assert result.status == VerificationStatus.MISSING_PRODUCT


def test_multi_product_exact_match():
    result = verify({"Pencil": 5, "Notebook": 3}, {"Pencil": 5, "Notebook": 3})
    assert result.status == VerificationStatus.VERIFIED
