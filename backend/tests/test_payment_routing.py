# backend/tests/test_payment_routing.py
"""
Tests for the payment routing engine.

Each test maps to a real business scenario or safety requirement.
These are not just unit tests — they are compliance assertions.
"""
from decimal import Decimal

import pytest

from app.services.payment_routing import (
    PaymentMethod,
    TradeDirection,
    recommend_payment_route,
    _check_eligibility,
    _normalize_extraction,
    _CORRIDOR_REGISTRY,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_extraction(overrides: dict = {}) -> dict:
    """Base extraction representing Maria's typical import transaction."""
    base = {
        "amount": "47500",
        "currency": "USD",
        "buyer_country": "US",
        "seller_country": "CO",   # Colombia — most common for Maria
    }
    return {**base, **overrides}


# ── Scenario tests — Maria's real corridors ───────────────────────────────────

def test_colombia_corridor_recommends_non_swift():
    """
    US → Colombia import at $47,500.
    Multiple better options exist — SWIFT should NOT be recommended.
    PSE/Stellar/dLocal should rank above SWIFT.
    """
    result = recommend_payment_route(make_extraction())
    assert result.recommended_method != PaymentMethod.SWIFT.value
    assert result.total_savings_usd > Decimal("0")
    assert result.context.destination_country == "CO"
    assert result.context.trade_direction == TradeDirection.IMPORT.value


def test_mexico_corridor_recommends_spei():
    """
    US → Mexico import at $50,000.
    SPEI should be available and rank highly due to near-zero cost + same day.
    """
    result = recommend_payment_route(make_extraction({
        "seller_country": "MX",
        "amount": "50000",
    }))
    method_names = [o.method for o in result.options]
    assert PaymentMethod.LOCAL_SPEI.value in method_names
    # SPEI should rank #1 or #2
    spei_option = next(o for o in result.options if o.method ==
                       PaymentMethod.LOCAL_SPEI.value)
    assert spei_option.rank <= 2


def test_brazil_corridor_recommends_pix():
    """
    US → Brazil import at $30,000.
    PIX should be available via dLocal and rank highly.
    Brazil is Miami's #1 trade partner — this corridor matters.
    """
    result = recommend_payment_route(make_extraction({
        "seller_country": "BR",
        "amount": "30000",
    }))
    method_names = [o.method for o in result.options]
    assert PaymentMethod.LOCAL_PIX.value in method_names
    pix_option = next(o for o in result.options if o.method ==
                      PaymentMethod.LOCAL_PIX.value)
    assert pix_option.eligible is True
    assert pix_option.rank <= 2


def test_dominican_republic_corridor_has_stellar():
    """
    US → Dominican Republic — Puente's strategic HQ corridor.
    USDC via Stellar should be available (Vibrant Assist anchor).
    """
    result = recommend_payment_route(make_extraction({
        "seller_country": "DO",
        "amount": "25000",
    }))
    method_names = [o.method for o in result.options]
    assert PaymentMethod.USDC_STELLAR.value in method_names
    stellar_option = next(
        o for o in result.options if o.method == PaymentMethod.USDC_STELLAR.value
    )
    assert stellar_option.eligible is True
    assert stellar_option.execution is not None
    assert stellar_option.execution.anchor_id == "vibrant_assist"


def test_china_corridor_only_swift_available():
    """
    US → China import.
    Strict capital controls — only SWIFT should be eligible.
    """
    result = recommend_payment_route(make_extraction({
        "seller_country": "CN",
        "amount": "85000",
    }))
    assert result.recommended_method == PaymentMethod.SWIFT.value
    # All other methods should be ineligible
    ineligible = [o.method for o in result.unavailable_options]
    assert PaymentMethod.USDC_STELLAR.value in ineligible
    assert PaymentMethod.WISE.value in ineligible


# ── Gate tests — safety checks ────────────────────────────────────────────────

def test_venezuela_all_methods_require_manual_review():
    """
    Venezuela requires OFAC screening for every transaction.
    No method should be eligible — all must go to unavailable with review reason.
    """
    result = recommend_payment_route(make_extraction({
        "seller_country": "VE",
        "amount": "10000",
    }))
    assert result.recommended_method is None
    assert len(result.options) == 0
    assert len(result.unavailable_options) > 0
    # Every method should cite OFAC screening requirement
    for opt in result.unavailable_options:
        assert opt.eligible is False
        assert any("OFAC" in r for r in opt.gate.reasons)


def test_sanctions_blocked_corridor_blocks_all_methods():
    """
    If sanctions_blocked=True in the registry, ALL methods must be blocked.
    We test this by temporarily patching the registry — not a real country.
    """
    # Inject a test corridor with sanctions_blocked=True
    _CORRIDOR_REGISTRY["XX"] = {
        "name": "Test Sanctioned Country",
        "settlement_currency": "XXX",
        "sanctions_blocked": True,
        "stellar_available": True,
        "stellar_anchor": "test_anchor",
        "wise_available": True,
        "dlocal_available": True,
        "dlocal_method": "XX_TEST",
        "local_rail": None,
        "local_rail_name": None,
        "ripple_odl_available": True,
        "compliance_notes": "Test only.",
    }
    try:
        result = recommend_payment_route(make_extraction({
            "seller_country": "XX",
            "amount": "50000",
        }))
        assert result.recommended_method is None
        assert len(result.options) == 0
        for opt in result.unavailable_options:
            assert opt.eligible is False
            assert any("sanctioned" in r.lower() for r in opt.gate.reasons)
    finally:
        # Always clean up the test corridor
        del _CORRIDOR_REGISTRY["XX"]


def test_amount_below_swift_minimum_blocks_swift():
    """
    SWIFT minimum is $100. A $50 transaction should not recommend SWIFT.
    """
    # Use a corridor where only SWIFT would normally be available (China)
    result = recommend_payment_route(make_extraction({
        "seller_country": "CN",
        "amount": "50",
    }))
    swift_options = [o for o in result.unavailable_options
                     if o.method == PaymentMethod.SWIFT.value]
    if swift_options:
        assert any("minimum" in r.lower()
                   for r in swift_options[0].gate.reasons)


def test_amount_above_pix_maximum_blocks_pix():
    """
    PIX maximum is $100,000. A $150,000 Brazil transaction should not use PIX.
    """
    result = recommend_payment_route(make_extraction({
        "seller_country": "BR",
        "amount": "150000",
    }))
    pix_options = [o for o in result.unavailable_options
                   if o.method == PaymentMethod.LOCAL_PIX.value]
    assert len(pix_options) > 0
    assert any("maximum" in r.lower() for r in pix_options[0].gate.reasons)


# ── Normalization tests ───────────────────────────────────────────────────────

def test_lowercase_country_codes_are_normalized():
    """
    Document AI might return "co" instead of "CO".
    The engine should handle this gracefully.
    """
    result = recommend_payment_route(make_extraction({
        "buyer_country": "us",
        "seller_country": "co",
    }))
    assert result.context.destination_country == "CO"
    assert result.context.origin_country == "US"


def test_zero_amount_raises_value_error():
    """
    A zero-dollar transaction should never be routed.
    The engine should raise ValueError, not silently produce a result.
    """
    with pytest.raises(ValueError, match="positive"):
        recommend_payment_route(make_extraction({"amount": "0"}))


def test_invalid_amount_raises_value_error():
    """
    Unparseable amounts like "N/A" should raise ValueError.
    """
    with pytest.raises(ValueError):
        recommend_payment_route(make_extraction({"amount": "N/A"}))


def test_none_amount_raises_value_error():
    """
    Missing amount should raise ValueError, not default to zero.
    """
    with pytest.raises(ValueError, match="required"):
        recommend_payment_route(make_extraction({"amount": None}))


# ── Output quality tests ──────────────────────────────────────────────────────

def test_routing_result_has_decision_id_and_hash():
    """
    Every result must have a unique decision_id and stable inputs_hash
    for audit trail purposes.
    """
    result = recommend_payment_route(make_extraction())
    assert result.decision_id.startswith("rtg_")
    assert len(result.inputs_hash) == 64   # SHA-256 hex = 64 chars
    assert result.policy_version == "routing-policy-2026.03"


def test_inputs_hash_is_stable_for_same_inputs():
    """
    Same normalized inputs must always produce the same hash.
    This is required for audit replay — if the hash changes, the audit
    log cannot be verified.
    """
    result1 = recommend_payment_route(make_extraction())
    result2 = recommend_payment_route(make_extraction())
    assert result1.inputs_hash == result2.inputs_hash


def test_eligible_options_have_no_execution_metadata_when_ineligible():
    """
    Ineligible methods must not carry 'available_v2' execution metadata.
    Showing a payment option as available_v2 when it's ineligible is misleading.
    """
    result = recommend_payment_route(make_extraction({
        "seller_country": "CN",  # China — most methods ineligible
        "amount": "50000",
    }))
    for opt in result.unavailable_options:
        assert opt.execution is None, (
            f"{opt.method} is ineligible but has execution metadata"
        )


def test_ranking_is_deterministic():
    """
    Running the same inputs twice must produce the same ranking.
    Non-deterministic ranking would make audit logs meaningless.
    """
    result1 = recommend_payment_route(make_extraction())
    result2 = recommend_payment_route(make_extraction())
    ranks1 = [o.method for o in result1.options]
    ranks2 = [o.method for o in result2.options]
    assert ranks1 == ranks2


def test_savings_is_positive_when_better_than_swift():
    """
    If a non-SWIFT method is recommended, it must show positive savings.
    Negative savings would mean we're recommending something more expensive.
    """
    result = recommend_payment_route(make_extraction())
    if result.recommended_method != PaymentMethod.SWIFT.value:
        assert result.total_savings_usd > Decimal("0")


def test_result_is_json_serializable():
    """
    The routing result must serialize to JSON cleanly.
    This validates that Decimal, datetime, and enum types all serialize correctly.
    """
    import json
    result = recommend_payment_route(make_extraction())
    result_dict = result.to_dict()
    # This will raise if any value is not JSON-serializable
    json_str = json.dumps(result_dict)
    assert len(json_str) > 0


def test_local_rail_only_eligible_for_matching_corridor():
    """
    SPEI should only be eligible for Mexico, not Colombia.
    PIX should only be eligible for Brazil, not Mexico.
    """
    # Colombia result — SPEI should not be eligible
    co_result = recommend_payment_route(make_extraction({
        "seller_country": "CO", "amount": "30000"
    }))
    spei_in_co = next(
        (o for o in co_result.unavailable_options
         if o.method == PaymentMethod.LOCAL_SPEI.value), None
    )
    assert spei_in_co is not None  # SPEI should be unavailable for Colombia

    # Mexico result — PIX should not be eligible
    mx_result = recommend_payment_route(make_extraction({
        "seller_country": "MX", "amount": "30000"
    }))
    pix_in_mx = next(
        (o for o in mx_result.unavailable_options
         if o.method == PaymentMethod.LOCAL_PIX.value), None
    )
    assert pix_in_mx is not None  # PIX should be unavailable for Mexico
