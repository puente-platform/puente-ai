# backend/app/models/onboarding.py
"""
Pydantic models for the onboarding profile resource.

Firestore path: users/{uid}
Fields stored:  displayName, company, corridors, completedAt, createdAt, updatedAt

Security notes:
- OnboardingProfileIn does NOT expose completedAt / createdAt / updatedAt;
  all timestamps are set server-side only (Security Constraint #2).
- uid / userId / sub in the request body are rejected at the Pydantic boundary
  (Security Constraint #1 — OWASP API1/BOLA).
- displayName and company are NFKC-normalized and control-char-rejected
  (Security Constraint #4 — OWASP API3/API8).
- Corridor IDs are enumerated against the six live corridors in
  frontend-app/src/lib/onboarding.ts:13-20 (Security Constraint #4).
"""

import unicodedata
from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints, field_validator, model_validator

# ---------------------------------------------------------------------------
# Corridor literal type — must match CORRIDOR_OPTIONS in onboarding.ts:13-20
# Six corridors as of 2026-04-30.
# ---------------------------------------------------------------------------
CorridorId = Literal[
    "mia-bog",
    "mia-sdq",
    "mia-sao",
    "mia-mex",
    "mia-lim",
    "mia-scl",
]

# ---------------------------------------------------------------------------
# Constrained string types — strip_whitespace happens before length check.
# ---------------------------------------------------------------------------
DisplayName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=80),
]
Company = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=120),
]

_CONTROL_CHAR_RE_RANGES = "\x00-\x1f\x7f"


def _nfkc_normalize(value: object) -> object:
    """
    NFKC-normalize a string before length validation. Runs in mode='before'
    on displayName/company so StringConstraints(max_length=...) sees the
    post-normalization length — otherwise compatibility expansions (e.g.
    U+FB03 'ﬃ' → 'ffi', or U+FDFA → 18 chars) can bypass the documented
    length limit. (bug_004 from ultrareview.)
    """
    if isinstance(value, str):
        return unicodedata.normalize("NFKC", value)
    return value


def _reject_control_chars(value: str | None, field_name: str) -> str | None:
    """
    Reject any control character (U+0000–U+001F or U+007F).
    Raises ValueError echoing only the field name, never the value.
    Runs in mode='after' on the already-NFKC-normalized, length-validated string.
    """
    if value is None:
        return value
    for ch in value:
        code = ord(ch)
        if code <= 0x1F or code == 0x7F:
            raise ValueError(
                f"Field '{field_name}' contains invalid characters."
            )
    return value


# ---------------------------------------------------------------------------
# Input model (client → server)
# ---------------------------------------------------------------------------

class OnboardingProfileIn(BaseModel):
    """
    All three data fields are Optional:
    - Missing key (not in model_fields_set) → preserve existing Firestore value.
    - Explicit null (None, in model_fields_set) → DELETE_FIELD sentinel.

    markComplete signals the server to set completedAt = SERVER_TIMESTAMP once,
    immutably. The client never supplies completedAt directly.
    """

    displayName: DisplayName | None = None
    company: Company | None = None
    corridors: list[CorridorId] | None = Field(default=None, max_length=7)
    markComplete: bool = False

    # ------------------------------------------------------------------
    # Security Constraint #1: reject uid / userId / sub in request body.
    # ------------------------------------------------------------------
    @model_validator(mode="before")
    @classmethod
    def reject_uid_fields(cls, data: object) -> object:
        if isinstance(data, dict):
            for forbidden in ("uid", "userId", "sub"):
                if forbidden in data:
                    raise ValueError(
                        f"Field '{forbidden}' is not allowed in request body."
                    )
        return data

    # ------------------------------------------------------------------
    # Security Constraint #4: NFKC normalize + length + control-char rejection.
    # NFKC runs mode='before' so StringConstraints sees post-normalization
    # length (bug_004 from ultrareview). Control-char check then runs
    # mode='after' on the already-validated string.
    # ------------------------------------------------------------------
    @field_validator("displayName", "company", mode="before")
    @classmethod
    def nfkc_normalize_text_fields(cls, v: object) -> object:
        return _nfkc_normalize(v)

    @field_validator("displayName", mode="after")
    @classmethod
    def reject_control_chars_in_display_name(cls, v: str | None) -> str | None:
        return _reject_control_chars(v, "displayName")

    @field_validator("company", mode="after")
    @classmethod
    def reject_control_chars_in_company(cls, v: str | None) -> str | None:
        return _reject_control_chars(v, "company")

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Output model (server → client)
# ---------------------------------------------------------------------------

class OnboardingProfileOut(BaseModel):
    """
    Response model returned by GET and POST /api/v1/onboarding.

    All timestamps are ISO 8601 strings set server-side.
    completedAt is None until the user marks onboarding complete.
    createdAt and updatedAt are always present on existing documents.
    """

    displayName: str | None = None
    company: str | None = None
    corridors: list[str] | None = None
    completedAt: str | None = None  # ISO 8601, server-set only
    createdAt: str  # ISO 8601, server-set on first write
    updatedAt: str  # ISO 8601, server-set on every write
