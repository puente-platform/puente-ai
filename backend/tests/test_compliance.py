# backend/tests/test_compliance.py
from app.services.compliance import check_compliance, ComplianceLevel


def make_extraction(overrides: dict | None = None) -> dict:
    """Base extraction with all docs present — should return HIGH (clean)."""
    base = {
        "amount": 10_000,
        "currency": "USD",
        "seller_country": "CN",
        "buyer_country": "US",
        "industry": "general",
        "has_commercial_invoice": True,
        "has_packing_list": True,
        "has_bill_of_lading": True,
        "has_certificate_of_origin": True,
        "has_cbp_entry": True,
        "has_isf_filing": True,
        "has_form_15ca": False,
        "has_export_license": False,
        "has_phyto_cert": False,
    }
    return {**base, **(overrides or {})}


# ── Demo scenario 1: Miami Textile → Mumbai ───────────────────────────────────
# $47,500 | Expected: MEDIUM (missing Form 15CA)

def test_scenario_1_miami_to_mumbai():
    extraction = make_extraction({
        "amount": 47_500,
        "seller_country": "IN",
        "buyer_country": "US",
        "industry": "textiles",
        "has_form_15ca": False,
        "has_cbp_entry": True,
        "has_isf_filing": True,
    })
    result = check_compliance(extraction)
    codes = [g.code for g in result.missing_documents]
    assert "IN_MISSING_FORM_15CA" in codes
    assert result.compliance_level == ComplianceLevel.MEDIUM


# ── Demo scenario 2: São Paulo Electronics → Shenzhen ────────────────────────
# $123,000 | Expected: LOW (missing export license — critical)

def test_scenario_2_electronics_dual_use():
    extraction = make_extraction({
        "amount": 123_000,
        "seller_country": "BR",
        "buyer_country": "CN",
        "industry": "electronics",
        "has_export_license": False,
        "has_cbp_entry": False,
        "has_isf_filing": False,
    })
    result = check_compliance(extraction)
    codes = [g.code for g in result.missing_documents]
    assert "MISSING_EXPORT_LICENSE" in codes
    assert result.compliance_level == ComplianceLevel.LOW


# ── Demo scenario 3: Mexico City Machinery → Delhi ───────────────────────────
# $85,000 | Expected: LOW (missing packing list + Form 15CA)

def test_scenario_3_mexico_to_delhi():
    extraction = make_extraction({
        "amount": 85_000,
        "seller_country": "IN",
        "buyer_country": "MX",
        "industry": "machinery",
        "has_packing_list": False,
        "has_form_15ca": False,
    })
    result = check_compliance(extraction)
    codes = [g.code for g in result.missing_documents]
    assert "MISSING_PACKING_LIST" in codes
    assert "IN_MISSING_FORM_15CA" in codes
    assert len(result.missing_documents) >= 2


# ── Demo scenario 4: Buenos Aires Agriculture → Shanghai ──────────────────────
# $200,000 | Expected: MEDIUM (missing phyto cert + high value warning)

def test_scenario_4_agriculture():
    extraction = make_extraction({
        "amount": 200_000,
        "seller_country": "AR",
        "buyer_country": "CN",
        "industry": "agriculture",
        "has_phyto_cert": False,
        "has_cbp_entry": False,
        "has_isf_filing": False,
    })
    result = check_compliance(extraction)
    codes = [g.code for g in result.missing_documents]
    assert "MISSING_PHYTO_CERT" in codes
    assert any("100,000" in w for w in result.warnings)


# ── Demo scenario 5: Bogotá Fashion → Bangalore ───────────────────────────────
# $32,000 | Expected: LOW (missing commercial invoice — critical)

def test_scenario_5_bogota_fashion():
    extraction = make_extraction({
        "amount": 32_000,
        "seller_country": "IN",
        "buyer_country": "CO",
        "industry": "fashion",
        "has_commercial_invoice": False,
        "has_form_15ca": False,
    })
    result = check_compliance(extraction)
    codes = [g.code for g in result.missing_documents]
    assert "MISSING_COMMERCIAL_INVOICE" in codes
    assert result.compliance_level == ComplianceLevel.LOW


# ── Edge cases ────────────────────────────────────────────────────────────────

def test_all_docs_present_returns_high():
    result = check_compliance(make_extraction())
    assert result.compliance_level == ComplianceLevel.HIGH
    assert len(result.missing_documents) == 0


def test_india_under_threshold_no_form_15ca_required():
    extraction = make_extraction({
        "amount": 20_000,
        "seller_country": "IN",
        "buyer_country": "US",
        "has_form_15ca": False,
    })
    result = check_compliance(extraction)
    codes = [g.code for g in result.missing_documents]
    assert "IN_MISSING_FORM_15CA" not in codes


def test_amount_with_comma_string_parses_safely():
    result = check_compliance(make_extraction({"amount": "10,000"}))
    assert result.compliance_level == ComplianceLevel.HIGH


def test_amount_with_invalid_string_defaults_to_zero():
    result = check_compliance(make_extraction({"amount": "N/A"}))
    assert result.compliance_level == ComplianceLevel.HIGH


def test_india_form_15ca_boundary():
    at_threshold = check_compliance(make_extraction({
        "amount": 25_000,
        "seller_country": "IN",
        "buyer_country": "US",
        "has_form_15ca": False,
    }))
    above_threshold = check_compliance(make_extraction({
        "amount": 25_000.01,
        "seller_country": "IN",
        "buyer_country": "US",
        "has_form_15ca": False,
    }))
    assert "IN_MISSING_FORM_15CA" not in [g.code for g in at_threshold.missing_documents]
    assert "IN_MISSING_FORM_15CA" in [g.code for g in above_threshold.missing_documents]


def test_us_cbp_entry_boundary():
    at_threshold = check_compliance(make_extraction({
        "amount": 2_500,
        "buyer_country": "US",
        "has_cbp_entry": False,
    }))
    above_threshold = check_compliance(make_extraction({
        "amount": 2_500.01,
        "buyer_country": "US",
        "has_cbp_entry": False,
    }))
    assert "US_MISSING_CBP_ENTRY" not in [g.code for g in at_threshold.missing_documents]
    assert "US_MISSING_CBP_ENTRY" in [g.code for g in above_threshold.missing_documents]


def test_unknown_string_boolean_is_not_treated_as_true():
    result = check_compliance(make_extraction({
        "has_commercial_invoice": "maybe",
    }))
    assert "MISSING_COMMERCIAL_INVOICE" in [g.code for g in result.missing_documents]


def test_us_import_missing_shipment_mode_adds_warning():
    result = check_compliance(make_extraction({
        "buyer_country": "US",
        "shipment_mode": "",
        "has_isf_filing": False,
    }))
    assert any("Shipment mode missing for US import" in w for w in result.warnings)


def test_us_isf_applies_only_to_ocean_shipments():
    air_result = check_compliance(make_extraction({
        "buyer_country": "US",
        "shipment_mode": "air",
        "has_isf_filing": False,
    }))
    ocean_result = check_compliance(make_extraction({
        "buyer_country": "US",
        "shipment_mode": "ocean",
        "has_isf_filing": False,
    }))
    assert "US_MISSING_ISF" not in [g.code for g in air_result.missing_documents]
    assert "US_MISSING_ISF" in [g.code for g in ocean_result.missing_documents]
