# backend/app/services/compliance.py
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class ComplianceLevel(str, Enum):
    LOW = "LOW"        # critical gaps — deal is blocked
    MEDIUM = "MEDIUM"  # high/medium gaps — proceed with caution
    HIGH = "HIGH"      # no gaps — clean


@dataclass
class ComplianceGap:
    code: str
    name: str
    severity: str      # "critical" | "high" | "medium" | "low"
    description: str
    action: str
    regulation: str
    estimated_fix_days: int = 1


@dataclass
class ComplianceResult:
    compliance_level: ComplianceLevel
    missing_documents: list[ComplianceGap] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    passed_checks: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "compliance_level": self.compliance_level.value,
            "gap_count": len(self.missing_documents),
            "missing_documents": [
                {
                    "code": g.code,
                    "name": g.name,
                    "severity": g.severity,
                    "description": g.description,
                    "action": g.action,
                    "regulation": g.regulation,
                    "estimated_fix_days": g.estimated_fix_days,
                }
                for g in self.missing_documents
            ],
            "warnings": self.warnings,
            "passed_checks": self.passed_checks,
        }


# ── constants ─────────────────────────────────────────────────────────────────

_AGRICULTURAL = {
    "agriculture", "food", "spices", "grain",
    "produce", "seafood", "seeds", "fertilizer",
}

_DUAL_USE = {
    "electronics", "semiconductors", "defense",
    "aerospace", "chemicals", "nuclear", "biotech",
}

_INDIA_FORM15CA_THRESHOLD_USD = 25_000
_HIGH_VALUE_THRESHOLD_USD = 100_000

_TRUE_SET = {"true", "1", "yes", "y", "on"}
_FALSE_SET = {"false", "0", "no", "n", "off", "", "none", "null"}


# ── input helpers ─────────────────────────────────────────────────────────────

def _safe_float(value: Any) -> float:
    """Convert any value to float safely. Returns 0.0 on failure."""
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return 0.0


def _as_bool(value: Any) -> bool:
    """
    Convert any value to bool safely.
    Handles string booleans like "true", "false", "yes" that
    Document AI may return.
    """
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        v = value.strip().lower()
        if v in _TRUE_SET:
            return True
        if v in _FALSE_SET:
            return False
        # Conservative default for unknown string-like booleans.
        return False
    return bool(value)


def _industry_tokens(industry: str) -> set[str]:
    """
    Split industry string into word tokens for safe set intersection.
    Prevents substring false-matches e.g. "bioelectronics" matching
    "electronics" via simple `in` check.
    """
    return set(re.findall(r"[a-z]+", industry.lower()))


# ── main checker ──────────────────────────────────────────────────────────────

def check_compliance(extraction: dict[str, Any]) -> ComplianceResult:
    """
    Rule-based compliance gap detector.

    Reads from the extraction dict. Boolean fields are normalised through
    _as_bool() so Document AI string values like "true"/"false" work correctly.
    Amount is parsed safely through _safe_float().

    Returns a ComplianceResult with compliance_level and missing_documents.
    """
    gaps: list[ComplianceGap] = []
    warnings: list[str] = []
    passed: list[str] = []

    # ── parse inputs ──────────────────────────────────────────────────────────
    amount_usd = _safe_float(extraction.get("amount"))
    currency = str(extraction.get("currency") or "USD").upper()
    seller = str(extraction.get("seller_country") or "").upper()
    buyer = str(extraction.get("buyer_country") or "").upper()
    industry = str(extraction.get("industry") or "").lower()
    tokens = _industry_tokens(industry)
    shipment_mode = str(extraction.get("shipment_mode") or "").strip().lower()

    has_commercial_invoice = _as_bool(extraction.get("has_commercial_invoice"))
    has_packing_list = _as_bool(extraction.get("has_packing_list"))
    has_bill_of_lading = _as_bool(extraction.get("has_bill_of_lading"))
    has_certificate_of_origin = _as_bool(
        extraction.get("has_certificate_of_origin"))
    has_form_15ca = _as_bool(extraction.get("has_form_15ca"))
    has_cbp_entry = _as_bool(extraction.get("has_cbp_entry"))
    has_isf_filing = _as_bool(extraction.get("has_isf_filing"))
    has_export_license = _as_bool(extraction.get("has_export_license"))
    has_phyto_cert = _as_bool(extraction.get("has_phyto_cert"))

    # Warn if non-USD — thresholds are USD-denominated
    if currency != "USD":
        warnings.append(
            "Amount treated as USD because FX conversion is not yet "
            "implemented. Threshold checks may be inaccurate."
        )

    # ── 1. Universal documents (every international shipment) ─────────────────
    if not has_commercial_invoice:
        gaps.append(ComplianceGap(
            code="MISSING_COMMERCIAL_INVOICE",
            name="Commercial Invoice",
            severity="critical",
            description="Required for all international trade transactions.",
            action="Obtain a signed commercial invoice from your supplier.",
            regulation="ICC Incoterms 2020",
            estimated_fix_days=1,
        ))
    else:
        passed.append("Commercial Invoice present")

    if not has_packing_list:
        gaps.append(ComplianceGap(
            code="MISSING_PACKING_LIST",
            name="Packing List",
            severity="critical",
            description="Required for all international shipments.",
            action="Request a detailed packing list from your supplier.",
            regulation="ICC Incoterms 2020",
            estimated_fix_days=1,
        ))
    else:
        passed.append("Packing List present")

    if not has_bill_of_lading:
        gaps.append(ComplianceGap(
            code="MISSING_BILL_OF_LADING",
            name="Bill of Lading / Airway Bill",
            severity="high",
            description="Proof of shipment contract between shipper and carrier.",
            action="Request Bill of Lading from your freight forwarder.",
            regulation="Carriage of Goods by Sea Act (COGSA)",
            estimated_fix_days=2,
        ))
    else:
        passed.append("Bill of Lading present")

    # ── 2. India corridor ─────────────────────────────────────────────────────
    if "IN" in (seller, buyer):
        if amount_usd > _INDIA_FORM15CA_THRESHOLD_USD:
            if not has_form_15ca:
                gaps.append(ComplianceGap(
                    code="IN_MISSING_FORM_15CA",
                    name="Form 15CA (RBI Foreign Remittance)",
                    severity="high",
                    description=(
                        f"RBI requires Form 15CA for foreign payments "
                        f"over ${_INDIA_FORM15CA_THRESHOLD_USD:,} USD."
                    ),
                    action=(
                        "File Form 15CA at incometaxindiaefiling.gov.in. "
                        "Your CA must also file Form 15CB."
                    ),
                    regulation="Income Tax Act Section 195; FEMA 1999",
                    estimated_fix_days=3,
                ))
            else:
                passed.append("Form 15CA present")

        if seller == "IN" and not has_certificate_of_origin:
            gaps.append(ComplianceGap(
                code="IN_MISSING_COO",
                name="Certificate of Origin (India)",
                severity="medium",
                description=(
                    "May qualify for preferential tariff rates under "
                    "trade agreements (SAFTA, ASEAN-India FTA)."
                ),
                action="Obtain from FIEO or Export Inspection Council.",
                regulation="Customs Act 1962; GSP Rules of Origin",
                estimated_fix_days=2,
            ))
        elif seller == "IN":
            passed.append("Certificate of Origin present")

        if amount_usd > 50_000:
            warnings.append(
                "Transactions over $50,000 to/from India may require "
                "additional FEMA reporting. Consult a CA."
            )

    # ── 3. US import corridor (buyer == US only — CBP/ISF are import rules) ───
    if buyer == "US":
        if amount_usd > 2_500 and not has_cbp_entry:
            gaps.append(ComplianceGap(
                code="US_MISSING_CBP_ENTRY",
                name="CBP Formal Entry (Form 7501)",
                severity="high",
                description="Required for US imports over $2,500.",
                action="File CBP Form 7501 via your licensed customs broker.",
                regulation="19 CFR Part 142",
                estimated_fix_days=1,
            ))
        elif amount_usd > 2_500:
            passed.append("CBP Formal Entry present")

        # ISF 10+2 only applies to ocean vessel imports, not air or land
        if shipment_mode in {"ocean", "sea"}:
            if not has_isf_filing:
                gaps.append(ComplianceGap(
                    code="US_MISSING_ISF",
                    name="Importer Security Filing (ISF 10+2)",
                    severity="high",
                    description=(
                        "Required 24 hours before vessel departure "
                        "for US ocean imports."
                    ),
                    action=(
                        "Submit ISF through your customs broker "
                        "via ACE portal."
                    ),
                    regulation="19 CFR Part 149",
                    estimated_fix_days=1,
                ))
            else:
                passed.append("ISF Filing present")
        elif not shipment_mode:
            warnings.append(
                "Shipment mode missing for US import. ISF applicability "
                "cannot be determined."
            )

    # ── 4. Agriculture ────────────────────────────────────────────────────────
    if tokens.intersection(_AGRICULTURAL):
        if not has_phyto_cert:
            gaps.append(ComplianceGap(
                code="MISSING_PHYTO_CERT",
                name="Phytosanitary Certificate",
                severity="high",
                description=(
                    "Government-issued certificate required for "
                    "agricultural goods."
                ),
                action=(
                    "Contact your national plant protection "
                    "organization (NPPO)."
                ),
                regulation="IPPC; USDA APHIS (US)",
                estimated_fix_days=5,
            ))
        else:
            passed.append("Phytosanitary Certificate present")

    # ── 5. Dual-use / export controls ─────────────────────────────────────────
    if tokens.intersection(_DUAL_USE):
        if not has_export_license:
            gaps.append(ComplianceGap(
                code="MISSING_EXPORT_LICENSE",
                name="Export Control License (BIS/EAR)",
                severity="critical",
                description=(
                    f"{industry.title()} goods may require a "
                    f"BIS/EAR export license."
                ),
                action=(
                    "File EAR license application at bis.doc.gov "
                    "before export."
                ),
                regulation=(
                    "Export Administration Regulations (EAR), "
                    "15 CFR 730-774"
                ),
                estimated_fix_days=30,
            ))
        else:
            passed.append("Export License present")

    # ── 6. High-value warning ─────────────────────────────────────────────────
    if amount_usd > _HIGH_VALUE_THRESHOLD_USD:
        warnings.append(
            "Transaction exceeds $100,000 USD. Enhanced due diligence "
            "may be required under BSA/AML regulations."
        )

    # ── 7. Derive compliance level from worst gap found ───────────────────────
    severities = {g.severity for g in gaps}
    if not gaps:
        level = ComplianceLevel.HIGH
    elif "critical" in severities:
        level = ComplianceLevel.LOW
    elif "high" in severities or "medium" in severities:
        level = ComplianceLevel.MEDIUM
    else:
        level = ComplianceLevel.HIGH

    logger.info(
        "Compliance check complete: level=%s gaps=%d",
        level.value,
        len(gaps),
    )

    return ComplianceResult(
        compliance_level=level,
        missing_documents=gaps,
        warnings=warnings,
        passed_checks=passed,
    )
