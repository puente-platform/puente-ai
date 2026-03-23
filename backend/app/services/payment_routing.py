# backend/app/services/payment_routing.py
from __future__ import annotations

import hashlib
import json
import logging
import uuid
from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)

# ── Money helper ──────────────────────────────────────────────────────────────
# One place where all Decimal rounding happens.
# ROUND_HALF_UP means $0.005 rounds to $0.01, not $0.00.
# This is the standard in financial systems — never use Python's
# default ROUND_HALF_EVEN (banker's rounding) for customer-facing amounts.


def _to_usd(value: Decimal) -> Decimal:
    """Round to 2 decimal places using standard financial rounding."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _to_pct(value: Decimal) -> Decimal:
    """Round to 4 decimal places for percentages (e.g. 0.0185 = 1.85%)."""
    return value.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


# ── Enums ─────────────────────────────────────────────────────────────────────
# Enums replace magic strings. Instead of checking `if method == "swift_wire"`
# scattered everywhere, we check `if method == PaymentMethod.SWIFT`.
# If you mistype an enum value Python tells you immediately.
# If you mistype a string, it silently fails.

class TradeDirection(str, Enum):
    IMPORT = "import"       # Maria is buying from a foreign supplier
    EXPORT = "export"       # Maria is selling to a foreign buyer
    UNKNOWN = "unknown"     # Direction not determinable from extraction


class GateStatus(str, Enum):
    PASS = "pass"           # Check passed, method is usable
    FAIL = "fail"           # Hard block — method cannot be used
    REVIEW = "review"       # Requires human review before proceeding


class QuoteStatus(str, Enum):
    STATIC = "static"       # V1: hardcoded estimate, not a live quote
    UNAVAILABLE = "unavailable"  # Method not available for this corridor


class PaymentMethod(str, Enum):
    SWIFT = "swift_wire"
    USDC_STELLAR = "usdc_stellar"
    WISE = "wise"
    DLOCAL = "dlocal"
    LOCAL_SPEI = "local_spei"       # Mexico
    LOCAL_PIX = "local_pix"         # Brazil
    LOCAL_PSE = "local_pse"         # Colombia
    RIPPLE_ODL = "ripple_odl"


# ── Context model ─────────────────────────────────────────────────────────────
# This is the normalized input to the routing engine.
# Raw extraction data is messy — Document AI might return "us" or "US" or "usa".
# The context model enforces clean, validated inputs before any logic runs.

class RoutingContext(BaseModel):
    """
    Normalized transaction context.
    All fields are validated and cleaned before the routing engine sees them.
    """
    model_config = ConfigDict(use_enum_values=True)

    origin_country: str = Field(
        min_length=2, max_length=2)       # ISO-2, uppercase
    destination_country: str = Field(min_length=2, max_length=2)
    payer_country: str = Field(min_length=2, max_length=2)
    beneficiary_country: str = Field(min_length=2, max_length=2)
    invoice_currency: str = Field(
        min_length=3, max_length=3)      # ISO-4217, e.g. "USD"
    settlement_currency: str = Field(min_length=3, max_length=3)
    amount: Decimal = Field(gt=Decimal("0"))
    trade_direction: TradeDirection


# ── Cost breakdown model ──────────────────────────────────────────────────────
# Splitting fees into components (flat + variable + FX spread) serves two purposes:
# 1. Transparency — Maria can see exactly what she's paying and why
# 2. Auditability — each component can be traced to a source/rule

class CostBreakdown(BaseModel):
    # Fixed cost regardless of amount
    flat_fee_usd: Optional[Decimal] = None
    # Percentage of transaction amount
    variable_fee_pct: Optional[Decimal] = None
    # FX markup on top of mid-market rate
    fx_spread_pct: Optional[Decimal] = None
    # The number Maria cares about
    total_cost_usd: Optional[Decimal] = None
    # total_cost / amount — apples-to-apples comparison
    effective_fee_pct: Optional[Decimal] = None


# ── Speed estimate model ──────────────────────────────────────────────────────
# A range (min/max) is more honest than a single number.
# "1-2 days" is more trustworthy than "1 day" when you can't guarantee it.
# confidence tells the UI how certain we are (0.0 = guess, 1.0 = guaranteed)

class SpeedEstimate(BaseModel):
    min_hours: Optional[int] = None
    max_hours: Optional[int] = None
    display: str                                  # Human-readable: "Same day to 2 days"
    confidence: float = Field(ge=0.0, le=1.0, default=0.7)


# ── V2 execution metadata ─────────────────────────────────────────────────────
# These fields are null in V1 but fully structured now so V2 can populate
# them without changing the schema. This is forward compatibility by design.
# The Stellar SEP-31 fields match the protocol spec exactly.

class ExecutionMetadata(BaseModel):
    protocol: str                                # e.g. "stellar_sep31", "wise_api"
    # "public" or "testnet" for Stellar
    network: Optional[str] = None
    anchor_id: Optional[str] = None             # e.g. "vibrant_assist"
    asset_code: Optional[str] = None            # "USDC"
    asset_issuer: Optional[str] = None          # Stellar USDC issuer address
    destination_currency: Optional[str] = None  # Local currency at destination
    requires_kyc: bool = True
    status: str = "available_v2"                # "available_v2" | "unavailable"


# ── Compliance gate result ────────────────────────────────────────────────────
# Each method goes through a gate check before being ranked.
# The gate result explains WHY a method is blocked, not just that it is.

class EligibilityGate(BaseModel):
    eligible: bool
    # Why it's blocked (shown to user if ineligible)
    reasons: list[str] = Field(default_factory=list)
    # What would make it eligible (e.g. "complete KYC")
    required_actions: list[str] = Field(default_factory=list)
    sanctions_check: GateStatus = GateStatus.PASS
    corridor_check: GateStatus = GateStatus.PASS


# ── Single payment option ─────────────────────────────────────────────────────

class PaymentOption(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    method: PaymentMethod
    display_name: str
    rank: Optional[int] = None
    eligible: bool
    gate: EligibilityGate
    quote_status: QuoteStatus
    cost: CostBreakdown
    speed: SpeedEstimate
    # null if this IS swift or unavailable
    savings_vs_swift_usd: Optional[Decimal] = None
    execution: Optional[ExecutionMetadata] = None

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")


# ── Final routing result ──────────────────────────────────────────────────────

class RoutingResult(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    decision_id: str                          # Unique ID for audit trail
    decision_time: datetime
    policy_version: str                       # Version of routing rules used
    context: RoutingContext
    recommended_method: Optional[str]         # None if no eligible route
    recommended_display: Optional[str]
    recommended_reason: str
    options: list[PaymentOption] = Field(
        default_factory=list)  # Eligible, ranked best first
    unavailable_options: list[PaymentOption] = Field(
        default_factory=list)  # Ineligible, with reasons
    total_savings_usd: Optional[Decimal] = None
    summary: str                              # Plain English for Maria
    disclaimer: str = (
        "Cost and speed estimates are based on typical rates for this corridor "
        "and are not guaranteed quotes. Actual fees may vary by provider."
    )
    inputs_hash: str                          # SHA-256 of inputs for audit replay

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")


# ── Corridor registry ─────────────────────────────────────────────────────────
# Each entry describes what's available for a destination country.
# This is intentionally a data structure, not logic — adding a new corridor
# means adding one entry here, not changing routing code.
#
# sanctions_blocked: True means NO payment method is available.
# We never recommend anything for sanctioned destinations — the gate
# catches this before any method is evaluated.

_CORRIDOR_REGISTRY: dict[str, dict] = {
    "CO": {
        "name": "Colombia",
        "settlement_currency": "COP",
        "sanctions_blocked": False,
        "stellar_available": True,
        "stellar_anchor": "vibrant_assist",
        "wise_available": True,
        "dlocal_available": True,
        "dlocal_method": "CO_PSE",
        "local_rail": PaymentMethod.LOCAL_PSE,
        "local_rail_name": "PSE / Nequi (Colombia)",
        "ripple_odl_available": True,
        "compliance_notes": (
            "Colombia requires beneficiary document ID for B2B transfers. "
            "Payments above ~$358K/year may trigger withholding for "
            "unregistered foreign entities."
        ),
    },
    "MX": {
        "name": "Mexico",
        "settlement_currency": "MXN",
        "sanctions_blocked": False,
        "stellar_available": True,
        "stellar_anchor": "bitso",
        "wise_available": True,
        "dlocal_available": True,
        "dlocal_method": "MX_SPEI",
        "local_rail": PaymentMethod.LOCAL_SPEI,
        "local_rail_name": "SPEI (Mexico)",
        "ripple_odl_available": True,
        "compliance_notes": (
            "SPEI is the dominant local rail — processed $61B in remittances "
            "in 2023. Near-instant, near-zero cost for MXN settlement."
        ),
    },
    "DO": {
        "name": "Dominican Republic",
        "settlement_currency": "DOP",
        "sanctions_blocked": False,
        "stellar_available": True,
        "stellar_anchor": "vibrant_assist",
        "wise_available": True,
        "dlocal_available": True,
        "dlocal_method": "DO_BANK",
        "local_rail": None,
        "local_rail_name": None,
        "ripple_odl_available": False,
        "compliance_notes": (
            "DR-CAFTA corridor. BCRD EPE license required for V2 execution. "
            "Off-ramp via Pagos al Instante (BCRD instant payment system)."
        ),
    },
    "PE": {
        "name": "Peru",
        "settlement_currency": "PEN",
        "sanctions_blocked": False,
        "stellar_available": True,
        "stellar_anchor": "anclap",
        "wise_available": True,
        "dlocal_available": True,
        "dlocal_method": "PE_BANK",
        "local_rail": None,
        "local_rail_name": None,
        "ripple_odl_available": False,
        "compliance_notes": None,
    },
    "BR": {
        "name": "Brazil",
        "settlement_currency": "BRL",
        "sanctions_blocked": False,
        "stellar_available": False,
        "stellar_anchor": None,
        "wise_available": True,
        "dlocal_available": True,
        "dlocal_method": "BR_PIX",
        "local_rail": PaymentMethod.LOCAL_PIX,
        "local_rail_name": "PIX (Brazil)",
        "ripple_odl_available": True,
        "compliance_notes": (
            "PIX processed $4.6T in 2024 — 42% of Brazilian e-commerce. "
            "Beneficiary CPF/CNPJ required for all transfers. "
            "SISCOMEX registration required for import declarations."
        ),
    },
    "GT": {
        "name": "Guatemala",
        "settlement_currency": "GTQ",
        "sanctions_blocked": False,
        "stellar_available": False,
        "stellar_anchor": None,
        "wise_available": True,
        "dlocal_available": False,
        "dlocal_method": None,
        "local_rail": None,
        "local_rail_name": None,
        "ripple_odl_available": False,
        "compliance_notes": None,
    },
    "SV": {
        "name": "El Salvador",
        "settlement_currency": "USD",   # dollarized economy
        "sanctions_blocked": False,
        "stellar_available": True,
        "stellar_anchor": None,          # no established anchor yet
        "wise_available": True,
        "dlocal_available": False,
        "dlocal_method": None,
        "local_rail": None,
        "local_rail_name": None,
        "ripple_odl_available": False,
        "compliance_notes": (
            "Dollarized economy — no FX conversion needed for USD settlement. "
            "Bitcoin legal tender since 2021."
        ),
    },
    "IN": {
        "name": "India",
        "settlement_currency": "INR",
        "sanctions_blocked": False,
        "stellar_available": False,
        "stellar_anchor": None,
        "wise_available": True,
        "dlocal_available": False,
        "dlocal_method": None,
        "local_rail": None,
        "local_rail_name": None,
        "ripple_odl_available": False,
        "compliance_notes": (
            "Form 15CA required for payments above $25,000 USD. "
            "UPI for domestic INR transfers only — not applicable for "
            "international B2B payments from US."
        ),
    },
    "CN": {
        "name": "China",
        "settlement_currency": "CNY",
        "sanctions_blocked": False,
        "stellar_available": False,
        "stellar_anchor": None,
        "wise_available": False,
        "dlocal_available": False,
        "dlocal_method": None,
        "local_rail": None,
        "local_rail_name": None,
        "ripple_odl_available": False,
        "compliance_notes": (
            "Strict capital controls. SWIFT wire via correspondent bank "
            "is the primary channel. PIPL data privacy compliance required "
            "for any data processed involving Chinese entities."
        ),
    },
    "VE": {
        "name": "Venezuela",
        "settlement_currency": "VES",
        "sanctions_blocked": False,      # Country not fully sanctioned
        "stellar_available": False,       # No established anchor
        "stellar_anchor": None,
        "wise_available": False,
        "dlocal_available": False,
        "dlocal_method": None,
        "local_rail": None,
        "local_rail_name": None,
        "ripple_odl_available": False,
        "compliance_notes": (
            "OFAC SDN list is dense with Venezuelan government-linked entities. "
            "Hard OFAC screening required before any payment. "
            "Trump oil blockade (Dec 2025) is reducing crypto liquidity. "
            "Manual review required for all Venezuelan transactions."
        ),
    },
}

# Used when destination country is not in the registry
_DEFAULT_CORRIDOR = {
    "name": "International",
    "settlement_currency": "USD",
    "sanctions_blocked": False,
    "stellar_available": False,
    "stellar_anchor": None,
    "wise_available": False,
    "dlocal_available": False,
    "dlocal_method": None,
    "local_rail": None,
    "local_rail_name": None,
    "ripple_odl_available": False,
    "compliance_notes": (
        "Corridor not fully mapped. SWIFT wire recommended as the "
        "universally available fallback."
    ),
}


# ── Transaction limits per method ─────────────────────────────────────────────
# These prevent recommending a method that will fail at execution.
# For example, recommending USDC for a $5 transaction is technically
# valid but the $0.50 flat fee makes it worse than SWIFT proportionally.
# Min/max are in USD.

_METHOD_LIMITS: dict[str, dict] = {
    PaymentMethod.SWIFT.value: {
        "min_usd": Decimal("100"),
        "max_usd": Decimal("10000000"),   # $10M — most banks
    },
    PaymentMethod.USDC_STELLAR.value: {
        "min_usd": Decimal("1"),
        "max_usd": Decimal("1000000"),
    },
    PaymentMethod.WISE.value: {
        "min_usd": Decimal("1"),
        "max_usd": Decimal("1000000"),
    },
    PaymentMethod.DLOCAL.value: {
        "min_usd": Decimal("10"),
        "max_usd": Decimal("500000"),
    },
    PaymentMethod.LOCAL_SPEI.value: {
        "min_usd": Decimal("1"),
        "max_usd": Decimal("300000"),
    },
    PaymentMethod.LOCAL_PIX.value: {
        "min_usd": Decimal("1"),
        "max_usd": Decimal("100000"),
    },
    PaymentMethod.LOCAL_PSE.value: {
        "min_usd": Decimal("1"),
        "max_usd": Decimal("100000"),
    },
    PaymentMethod.RIPPLE_ODL.value: {
        "min_usd": Decimal("100"),
        "max_usd": Decimal("1000000"),
    },
}


# ── Eligibility gate ──────────────────────────────────────────────────────────
# This runs BEFORE ranking. A method that fails a gate never enters
# the ranking pool — it goes into unavailable_options with a reason.
#
# V1 gates (implemented now):
#   - Venezuela manual review flag
#   - Amount limits per method
#   - Corridor availability check
#
# V2 gates (stubs returning PASS for now):
#   - Live OFAC API screening
#   - KYC tier check
#   - Anchor operational status

def _check_eligibility(
    method: PaymentMethod,
    amount: Decimal,
    destination_country: str,
    corridor: dict,
) -> EligibilityGate:
    """
    Run all eligibility checks for a single payment method.
    Returns an EligibilityGate with eligible=True only if ALL checks pass.
    """
    reasons: list[str] = []
    required_actions: list[str] = []
    sanctions_status = GateStatus.PASS
    corridor_status = GateStatus.PASS

    # ── Gate 1: Venezuela manual review ──────────────────────────────────────
    # Venezuela is not fully sanctioned but OFAC SDN list is dense with
    # government-linked entities. We flag for manual review rather than
    # blocking entirely — a legitimate private business transaction is
    # possible but requires human verification first.

    # ── Gate 0: Hard sanctions block ─────────────────────────────────────────
# If the corridor registry marks this destination as sanctions_blocked,
# no payment method is available — fail all methods immediately.
    if corridor.get("sanctions_blocked", False):
        return EligibilityGate(
            eligible=False,
            reasons=[
                f"{corridor.get('name', destination_country)} is currently "
                f"sanctioned. No payment method is available."
            ],
            required_actions=["contact_compliance_team"],
            sanctions_check=GateStatus.FAIL,
            corridor_check=GateStatus.FAIL,
        )

    if destination_country == "VE":
        reasons.append(
            "Venezuela transactions require manual OFAC screening before "
            "any payment method can be recommended."
        )
        required_actions.append("complete_ofac_manual_review")
        sanctions_status = GateStatus.REVIEW
        return EligibilityGate(
            eligible=False,
            reasons=reasons,
            required_actions=required_actions,
            sanctions_check=sanctions_status,
            corridor_check=corridor_status,
        )

    # ── Gate 2: Corridor availability ────────────────────────────────────────
    # Check if this specific method is available for this destination.
    method_available = {
        PaymentMethod.SWIFT: True,          # SWIFT always structurally available
        PaymentMethod.USDC_STELLAR: corridor.get("stellar_available", False),
        PaymentMethod.WISE: corridor.get("wise_available", False),
        PaymentMethod.DLOCAL: corridor.get("dlocal_available", False),
        PaymentMethod.LOCAL_SPEI: corridor.get("local_rail") == PaymentMethod.LOCAL_SPEI,
        PaymentMethod.LOCAL_PIX: corridor.get("local_rail") == PaymentMethod.LOCAL_PIX,
        PaymentMethod.LOCAL_PSE: corridor.get("local_rail") == PaymentMethod.LOCAL_PSE,
        PaymentMethod.RIPPLE_ODL: corridor.get("ripple_odl_available", False),
    }.get(method, False)

    if not method_available:
        reasons.append(
            f"{method.value} is not available for the "
            f"{corridor.get('name', destination_country)} corridor."
        )
        corridor_status = GateStatus.FAIL

    # ── Gate 3: Amount limits ─────────────────────────────────────────────────
    limits = _METHOD_LIMITS.get(method.value, {})
    min_usd = limits.get("min_usd", Decimal("0"))
    max_usd = limits.get("max_usd", Decimal("99999999"))

    if amount < min_usd:
        reasons.append(
            f"{method.value} minimum transaction is "
            f"${min_usd:,.0f} USD. This transaction is ${amount:,.2f}."
        )
    elif amount > max_usd:
        reasons.append(
            f"{method.value} maximum transaction is "
            f"${max_usd:,.0f} USD. This transaction is ${amount:,.2f}."
        )

    # ── Gate 4: OFAC stub (V2 will call live API) ─────────────────────────────
    # In V2 this becomes an actual OFAC API call.
    # For now it always passes — we document the gap explicitly.
    # TODO(V2): integrate live OFAC SDN screening here
    ofac_pass = True   # noqa: placeholder

    eligible = (
        len(reasons) == 0
        and corridor_status == GateStatus.PASS
        and ofac_pass
    )

    return EligibilityGate(
        eligible=eligible,
        reasons=reasons,
        required_actions=required_actions,
        sanctions_check=sanctions_status,
        corridor_check=corridor_status,
    )

# ── Static fee models ─────────────────────────────────────────────────────────
# V1 uses static estimates with a clear disclaimer.
# V2 replaces these with live quote adapters per provider.
# All values use Decimal — no floats anywhere in fee math.


_FEE_MODELS: dict[str, dict] = {
    PaymentMethod.SWIFT.value: {
        "flat_fee_usd": Decimal("45"),
        "fx_spread_pct": Decimal("0.018"),    # 1.8% average FX spread
        "speed_min_hours": 72,                 # 3 business days
        "speed_max_hours": 120,                # 5 business days
        "speed_display": "3–5 business days",
        "reliability_score": Decimal("0.95"),  # Highly reliable, just slow
        "compliance_score": Decimal("0.80"),   # Heavy KYC/AML burden
    },
    PaymentMethod.USDC_STELLAR.value: {
        "flat_fee_usd": Decimal("0.50"),
        "fx_spread_pct": Decimal("0.005"),     # 0.5% off-ramp cost
        "speed_min_hours": 1,
        "speed_max_hours": 36,                 # On-chain instant, off-ramp varies
        "speed_display": "Hours to ~1.5 days",
        "reliability_score": Decimal("0.80"),  # Anchor dependency
        "compliance_score": Decimal("0.85"),
    },
    PaymentMethod.WISE.value: {
        "flat_fee_usd": Decimal("0"),
        "fx_spread_pct": Decimal("0.008"),     # ~0.8% average
        "speed_min_hours": 24,
        "speed_max_hours": 48,
        "speed_display": "1–2 business days",
        "reliability_score": Decimal("0.92"),
        "compliance_score": Decimal("0.90"),
    },
    PaymentMethod.DLOCAL.value: {
        "flat_fee_usd": Decimal("5"),
        "fx_spread_pct": Decimal("0.010"),     # ~1.0%
        "speed_min_hours": 1,
        "speed_max_hours": 24,
        "speed_display": "Same day to 1 day",
        "reliability_score": Decimal("0.88"),
        "compliance_score": Decimal("0.88"),
    },
    PaymentMethod.LOCAL_SPEI.value: {
        "flat_fee_usd": Decimal("2"),
        "fx_spread_pct": Decimal("0.001"),     # Near-zero
        "speed_min_hours": 0,
        "speed_max_hours": 4,
        "speed_display": "Same day (SPEI)",
        "reliability_score": Decimal("0.95"),
        "compliance_score": Decimal("0.92"),
    },
    PaymentMethod.LOCAL_PIX.value: {
        "flat_fee_usd": Decimal("2"),
        "fx_spread_pct": Decimal("0.001"),
        "speed_min_hours": 0,
        "speed_max_hours": 2,
        "speed_display": "Instant (PIX)",
        "reliability_score": Decimal("0.97"),
        "compliance_score": Decimal("0.90"),
    },
    PaymentMethod.LOCAL_PSE.value: {
        "flat_fee_usd": Decimal("2"),
        "fx_spread_pct": Decimal("0.002"),
        "speed_min_hours": 0,
        "speed_max_hours": 8,
        "speed_display": "Same day (PSE/Nequi)",
        "reliability_score": Decimal("0.88"),
        "compliance_score": Decimal("0.88"),
    },
    PaymentMethod.RIPPLE_ODL.value: {
        "flat_fee_usd": Decimal("0.01"),
        "fx_spread_pct": Decimal("0.003"),
        "speed_min_hours": 0,
        "speed_max_hours": 1,
        "speed_display": "~4 seconds on-chain",
        "reliability_score": Decimal("0.82"),
        "compliance_score": Decimal("0.83"),
    },
}

# Ranking weights — must sum to 1.0
_WEIGHT_COST = Decimal("0.40")
_WEIGHT_SPEED = Decimal("0.20")
_WEIGHT_RELIABILITY = Decimal("0.20")
_WEIGHT_COMPLIANCE = Decimal("0.20")

# Fixed priority order for tie-breaking — lower index = preferred
_METHOD_TIEBREAK_ORDER = [
    PaymentMethod.LOCAL_SPEI,
    PaymentMethod.LOCAL_PIX,
    PaymentMethod.LOCAL_PSE,
    PaymentMethod.USDC_STELLAR,
    PaymentMethod.DLOCAL,
    PaymentMethod.RIPPLE_ODL,
    PaymentMethod.WISE,
    PaymentMethod.SWIFT,
]

# Routing policy version — bump this when rules change so audit logs
# can identify which version of the policy made a given decision
_POLICY_VERSION = "routing-policy-2026.03"


# ── Input normalization ───────────────────────────────────────────────────────

def _normalize_extraction(extraction: dict[str, Any]) -> RoutingContext:
    """
    Convert raw extraction dict to a validated RoutingContext.
    Uppercases and strips all country/currency codes.
    Raises ValueError if inputs are unusable.
    """
    def _clean_country(value: Any) -> str:
        if not value:
            # TODO(V2): raise ValueError here once extraction quality is validated
            # For V1, default to US to avoid crashing on incomplete Document AI output
            logger.warning(
                "Missing country code in extraction — defaulting to US")
            return "US"
        cleaned = str(value).strip().upper()
        if len(cleaned) != 2:
            logger.warning(
                "Invalid country code '%s' — defaulting to US", value)
            return "US"
        return cleaned

    def _clean_currency(value: Any) -> str:
        if not value:
            return "USD"
        return str(value).strip().upper()[:3]

    def _safe_decimal(value: Any) -> Decimal:
        if value is None:
            raise ValueError(
                "Transaction amount is required for payment routing.")
        if isinstance(value, Decimal):
            if value <= 0:
                raise ValueError(
                    f"Transaction amount must be positive, got {value}.")
            return value
        try:
            result = Decimal(str(value).replace(",", "").strip())
            if result <= 0:
                raise ValueError(
                    f"Transaction amount must be positive, got {result}.")
            return result
        except Exception as e:
            raise ValueError(
                f"Cannot parse transaction amount '{value}': {e}") from e

    buyer = _clean_country(extraction.get("buyer_country"))
    seller = _clean_country(extraction.get("seller_country"))

    # Determine trade direction and corridor
    # Maria is US-based — if buyer is US, she's importing (paying a foreign seller)
    # If seller is US, she's exporting (receiving payment from a foreign buyer)
    if buyer == "US":
        origin = "US"
        destination = seller
        payer = "US"
        beneficiary = seller
        direction = TradeDirection.IMPORT
    elif seller == "US":
        origin = "US"
        destination = buyer
        payer = buyer
        beneficiary = "US"
        direction = TradeDirection.EXPORT
    else:
        # Neither party is US — cross-border between two foreign countries
        origin = seller
        destination = buyer
        payer = buyer
        beneficiary = seller
        direction = TradeDirection.UNKNOWN

    amount = _safe_decimal(extraction.get("amount"))
    invoice_currency = _clean_currency(extraction.get("currency"))

    # Look up settlement currency from corridor registry
    corridor = _CORRIDOR_REGISTRY.get(destination, _DEFAULT_CORRIDOR)
    settlement_currency = corridor.get("settlement_currency", "USD")

    return RoutingContext(
        origin_country=origin,
        destination_country=destination,
        payer_country=payer,
        beneficiary_country=beneficiary,
        invoice_currency=invoice_currency,
        settlement_currency=settlement_currency,
        amount=amount,
        trade_direction=direction,
    )


# ── Cost computation ──────────────────────────────────────────────────────────

def _compute_cost(method: PaymentMethod, amount: Decimal) -> CostBreakdown:
    """Compute cost breakdown for a payment method at a given amount."""
    model = _FEE_MODELS.get(method.value, {})
    flat = model.get("flat_fee_usd", Decimal("0"))
    spread = model.get("fx_spread_pct", Decimal("0"))

    total = _to_usd(flat + (amount * spread))
    effective_pct = _to_pct(total / amount) if amount > 0 else Decimal("0")

    return CostBreakdown(
        flat_fee_usd=_to_usd(flat),
        variable_fee_pct=None,
        fx_spread_pct=_to_pct(spread),
        total_cost_usd=total,
        effective_fee_pct=effective_pct,
    )


# ── Ranking score ─────────────────────────────────────────────────────────────

def _compute_score(
    method: PaymentMethod,
    cost: CostBreakdown,
    swift_cost: CostBreakdown,
    all_costs: list[Decimal],
    all_speeds: list[int],
) -> Decimal:
    """
    Compute a weighted ranking score (0.0–1.0, higher = better).

    Cost score: how much cheaper vs the most expensive option
    Speed score: how much faster vs the slowest option
    Reliability + compliance: from the fee model static values
    """
    model = _FEE_MODELS.get(method.value, {})

    # Cost score — normalized: 0 = most expensive, 1 = cheapest
    max_cost = max(all_costs) if all_costs else Decimal("1")
    min_cost = min(all_costs) if all_costs else Decimal("0")
    cost_range = max_cost - min_cost
    method_cost = cost.total_cost_usd or Decimal("0")

    if cost_range > 0:
        cost_score = (max_cost - method_cost) / cost_range
    else:
        cost_score = Decimal("1")

    # Speed score — normalized: 0 = slowest, 1 = fastest
    max_speed = Decimal(max(all_speeds)) if all_speeds else Decimal("1")
    min_speed = Decimal(min(all_speeds)) if all_speeds else Decimal("0")
    speed_range = max_speed - min_speed
    method_speed = Decimal(
        _FEE_MODELS.get(method.value, {}).get("speed_max_hours", Decimal("120"))
    )

    if speed_range > Decimal("0"):
        speed_score = (max_speed - method_speed) / speed_range
    else:
        speed_score = Decimal("1")

    reliability = model.get("reliability_score", Decimal("0.5"))
    compliance = model.get("compliance_score", Decimal("0.5"))

    score = (
        _WEIGHT_COST * cost_score
        + _WEIGHT_SPEED * speed_score
        + _WEIGHT_RELIABILITY * reliability
        + _WEIGHT_COMPLIANCE * compliance
    )

    return _to_pct(score)


# ── Main entrypoint ───────────────────────────────────────────────────────────

def recommend_payment_route(extraction: dict[str, Any]) -> RoutingResult:
    """
    Generate a payment routing recommendation from raw extraction data.

    This is the only public function in this module.
    Everything else is internal implementation detail.

    Args:
        extraction: raw dict from Document AI / Gemini analysis

    Returns:
        RoutingResult with ranked options and a plain-English summary
    """
    # ── Step 1: Normalize inputs ──────────────────────────────────────────────
    context = _normalize_extraction(extraction)
    corridor = _CORRIDOR_REGISTRY.get(
        context.destination_country, _DEFAULT_CORRIDOR
    )

    # ── Step 2: Generate decision metadata ────────────────────────────────────
    decision_id = f"rtg_{uuid.uuid4().hex[:12]}"
    decision_time = datetime.now(timezone.utc)

    # Inputs hash — SHA-256 of the normalized context for audit replay
    inputs_payload = json.dumps({
        "destination": context.destination_country,
        "amount": str(context.amount),
        "currency": context.invoice_currency,
        "direction": context.trade_direction,
    }, sort_keys=True)
    inputs_hash = hashlib.sha256(inputs_payload.encode()).hexdigest()

    # ── Step 3: Compute SWIFT cost as baseline ────────────────────────────────
    swift_cost = _compute_cost(PaymentMethod.SWIFT, context.amount)

    # ── Step 4: Evaluate all methods ─────────────────────────────────────────
    eligible_options: list[PaymentOption] = []
    unavailable_options: list[PaymentOption] = []

    # Pre-compute costs and speeds for eligible methods (needed for normalization)
    eligible_costs: list[Decimal] = []
    eligible_speeds: list[int] = []

    # First pass — check eligibility and compute costs
    method_data: list[tuple[PaymentMethod,
                            EligibilityGate, CostBreakdown]] = []

    for method in PaymentMethod:
        gate = _check_eligibility(
            method=method,
            amount=context.amount,
            destination_country=context.destination_country,
            corridor=corridor,
        )
        cost = _compute_cost(
            method, context.amount) if gate.eligible else CostBreakdown()

        if gate.eligible:
            eligible_costs.append(cost.total_cost_usd or Decimal("0"))
            speed_max = _FEE_MODELS.get(
                method.value, {}).get("speed_max_hours", 120)
            eligible_speeds.append(speed_max)

        method_data.append((method, gate, cost))

    # Second pass — build PaymentOption objects with scores
    for method, gate, cost in method_data:
        fee_model = _FEE_MODELS.get(method.value, {})
        savings = None
        if gate.eligible and method != PaymentMethod.SWIFT:
            savings = _to_usd(
                (swift_cost.total_cost_usd or Decimal("0"))
                - (cost.total_cost_usd or Decimal("0"))
            )

        # Build execution metadata for methods that support V2 execution
        execution = _build_execution_metadata(
            method, corridor) if gate.eligible else None

        option = PaymentOption(
            method=method,
            display_name=_METHOD_DISPLAY_NAMES[method],
            eligible=gate.eligible,
            gate=gate,
            quote_status=QuoteStatus.STATIC if gate.eligible else QuoteStatus.UNAVAILABLE,
            cost=cost,
            speed=SpeedEstimate(
                min_hours=fee_model.get("speed_min_hours"),
                max_hours=fee_model.get("speed_max_hours"),
                display=fee_model.get("speed_display", "Unknown"),
                confidence=0.7,
            ),
            savings_vs_swift_usd=savings,
            execution=execution,
        )

        if gate.eligible:
            eligible_options.append(option)
        else:
            unavailable_options.append(option)

    # ── Step 5: Rank eligible options ─────────────────────────────────────────
    def _sort_key(opt: PaymentOption) -> tuple:
        score = _compute_score(
            method=PaymentMethod(opt.method),
            cost=opt.cost,
            swift_cost=swift_cost,
            all_costs=eligible_costs,
            all_speeds=eligible_speeds,
        )
        tiebreak = _METHOD_TIEBREAK_ORDER.index(PaymentMethod(opt.method)) \
            if PaymentMethod(opt.method) in _METHOD_TIEBREAK_ORDER else 99
        # Negate score so highest score sorts first
        return (-score, tiebreak)

    eligible_options.sort(key=_sort_key)

    # Assign ranks
    for i, opt in enumerate(eligible_options):
        opt.rank = i + 1

    # ── Step 6: Handle no eligible routes ─────────────────────────────────────
    if not eligible_options:
        return RoutingResult(
            decision_id=decision_id,
            decision_time=decision_time,
            policy_version=_POLICY_VERSION,
            context=context,
            recommended_method=None,
            recommended_display=None,
            recommended_reason="No eligible payment route found. Manual review required.",
            options=[],
            unavailable_options=unavailable_options,
            total_savings_usd=None,
            summary=(
                "No payment route could be recommended for this transaction. "
                "Please contact support for manual processing."
            ),
            inputs_hash=inputs_hash,
        )

    # ── Step 7: Build result ───────────────────────────────────────────────────
    best = eligible_options[0]
    total_savings = best.savings_vs_swift_usd or Decimal("0")

    if total_savings > 0 and best.method != PaymentMethod.SWIFT.value:
        time_str = _time_saved(best)
        if time_str == "no time saved":
            summary = (
                f"Estimated savings of ${total_savings:,.2f} by using "
                f"{best.display_name} instead of a bank wire."
            )
        else:
            summary = (
                f"Estimated savings of ${total_savings:,.2f} and "
                f"{time_str} by using "
                f"{best.display_name} instead of a bank wire."
            )
        reason = f"Best weighted score among eligible routes for the {corridor.get('name', context.destination_country)} corridor."
    else:
        summary = (
            f"Bank wire (SWIFT) is the recommended option for this corridor. "
            f"Estimated fee: ${(swift_cost.total_cost_usd or Decimal('0')):,.2f}."
        )
        reason = "SWIFT is the recommended route for this corridor."

    logger.info(
        "Routing decision %s: recommended=%s corridor=%s amount=$%s savings=$%s",
        decision_id,
        best.method,
        context.destination_country,
        f"{context.amount:.2f}",
        f"{total_savings:.2f}",
    )

    return RoutingResult(
        decision_id=decision_id,
        decision_time=decision_time,
        policy_version=_POLICY_VERSION,
        context=context,
        recommended_method=best.method,
        recommended_display=best.display_name,
        recommended_reason=reason,
        options=eligible_options,
        unavailable_options=unavailable_options,
        total_savings_usd=total_savings,
        summary=summary,
        inputs_hash=inputs_hash,
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

_METHOD_DISPLAY_NAMES: dict[PaymentMethod, str] = {
    PaymentMethod.SWIFT: "Traditional Bank Wire (SWIFT)",
    PaymentMethod.USDC_STELLAR: "USDC via Stellar Network",
    PaymentMethod.WISE: "Wise (International Transfer)",
    PaymentMethod.DLOCAL: "dLocal (Local Payment Rails)",
    PaymentMethod.LOCAL_SPEI: "SPEI (Mexico Instant Transfer)",
    PaymentMethod.LOCAL_PIX: "PIX (Brazil Instant Transfer)",
    PaymentMethod.LOCAL_PSE: "PSE / Nequi (Colombia)",
    PaymentMethod.RIPPLE_ODL: "Ripple ODL (XRP On-Demand Liquidity)",
}


def _build_execution_metadata(
    method: PaymentMethod,
    corridor: dict,
) -> ExecutionMetadata | None:
    """Build V2 execution metadata for methods that support it."""
    if method == PaymentMethod.USDC_STELLAR:
        anchor = corridor.get("stellar_anchor")
        return ExecutionMetadata(
            protocol="stellar_sep31",
            network="public",
            anchor_id=anchor,
            asset_code="USDC",
            asset_issuer="GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN",
            destination_currency=corridor.get("settlement_currency"),
            requires_kyc=True,
            status="available_v2" if anchor else "unavailable",
        )
    if method == PaymentMethod.WISE:
        return ExecutionMetadata(
            protocol="wise_api",
            status="available_v2",
        )
    if method == PaymentMethod.DLOCAL:
        return ExecutionMetadata(
            protocol="dlocal_api",
            status="available_v2",
        )
    if method in (
        PaymentMethod.LOCAL_SPEI,
        PaymentMethod.LOCAL_PIX,
        PaymentMethod.LOCAL_PSE,
    ):
        return ExecutionMetadata(
            protocol=method.value,
            status="available_v2",
        )
    if method == PaymentMethod.RIPPLE_ODL:
        return ExecutionMetadata(
            protocol="ripple_odl",
            status="available_v2",
        )
    return None  # SWIFT is bank-handled, no Puente execution metadata


def _time_saved(best: PaymentOption) -> str:
    """Generate human-readable time saved string."""
    swift_hours = _FEE_MODELS[PaymentMethod.SWIFT.value]["speed_max_hours"]

    method_key = best.method if isinstance(
        best.method, str) else best.method.value
    best_hours = _FEE_MODELS.get(method_key, {}).get(
        "speed_max_hours", swift_hours)

    hours_saved = swift_hours - best_hours
    if hours_saved <= 0:
        return "no time saved"
    days = hours_saved // 24
    if days == 1:
        return "1 day faster"
    if days > 1:
        return f"{days} days faster"
    return f"{hours_saved} hours faster"
