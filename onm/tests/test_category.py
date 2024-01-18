import pytest
from onm.category import (
    ONM_STANDARD_CATEGORIES,
    APPLE_ONM_CATEGORY_MAPPING,
    AMEX_ONM_CATEGORY_MAPPING,
    MINT_ONM_CATEGORY_MAPPING,
    get_onm_category,
)

pytestmark = pytest.mark.unit


def test_apple_onm_category_mapping():
    for category in APPLE_ONM_CATEGORY_MAPPING.values():
        assert category in ONM_STANDARD_CATEGORIES


def test_amex_onm_category_mapping():
    for category in AMEX_ONM_CATEGORY_MAPPING.values():
        assert category in ONM_STANDARD_CATEGORIES


def test_mint_onm_category_mapping():
    for category in MINT_ONM_CATEGORY_MAPPING.values():
        assert category in ONM_STANDARD_CATEGORIES


def test_get_onm_category():
    assert "TRANSPORTATION" == get_onm_category(
        "Transportation", None, APPLE_ONM_CATEGORY_MAPPING
    )
    assert "TRANSFER_IN:OTHER_TRANSFER_IN" == get_onm_category(
        "Payment", None, APPLE_ONM_CATEGORY_MAPPING
    )
    assert "UNKNOWN" == get_onm_category("Business", None, APPLE_ONM_CATEGORY_MAPPING)
    assert "RENT_AND_UTILITIES:TELEPHONE" == get_onm_category(
        "Communications", "Mobile", AMEX_ONM_CATEGORY_MAPPING
    )
    assert "BANK_FEES" == get_onm_category(
        "Fees & Adjustments", None, AMEX_ONM_CATEGORY_MAPPING
    )
    assert "LOAN_PAYMENTS:CAR_PAYMENT" == get_onm_category(
        "Auto & Transport", "Auto Payment", MINT_ONM_CATEGORY_MAPPING
    )
    assert "TRANSPORTATION" == get_onm_category(
        "Auto & Transport", "Auto Payments", MINT_ONM_CATEGORY_MAPPING
    )
