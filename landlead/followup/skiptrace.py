"""Skip-trace connector hooks — placeholder integrations.

Skip tracing locates a person's current contact info from regulated data
sources. Doing so requires a PERMISSIBLE PURPOSE under GLBA/DPPA/FCRA. Real
estate marketing is commonly treated as permissible, but you are responsible for
confirming that with your vendor and counsel BEFORE enabling a provider.

This module ships as clearly-marked seams for TLO, BatchSkipTracing, and IDI.
No provider is active unless SKIPTRACE_PROVIDER is set and its API key is
present. Each connector raises a clear NotImplementedError with the exact spot
to wire the vendor call, so nothing silently pretends to trace.
"""
from __future__ import annotations

from config.settings import get_settings
from db import repo


class SkipTraceError(RuntimeError):
    pass


def _require_provider() -> tuple[str, str]:
    settings = get_settings()
    provider = settings.SKIPTRACE_PROVIDER
    if not provider:
        raise SkipTraceError(
            "No skip-trace provider configured. Set SKIPTRACE_PROVIDER "
            "(tlo|batchskiptracing|idi) and the matching API key. See COMPLIANCE.md."
        )
    key = settings.SKIPTRACE_KEYS.get(provider, "")
    if not key:
        raise SkipTraceError(f"SKIPTRACE_PROVIDER={provider} but its API key is empty.")
    return provider, key


# --- vendor connectors (wire your real call inside each) --------------------
def _trace_tlo(lead: dict, api_key: str) -> list[dict]:
    raise NotImplementedError(
        "Wire the TLO/TransUnion API call here. Return a list of "
        "{name, phone, email, mailing_address, confidence} dicts."
    )


def _trace_batchskiptracing(lead: dict, api_key: str) -> list[dict]:
    raise NotImplementedError(
        "Wire the BatchSkipTracing API call here. Return a list of "
        "{name, phone, email, mailing_address, confidence} dicts."
    )


def _trace_idi(lead: dict, api_key: str) -> list[dict]:
    raise NotImplementedError(
        "Wire the IDI/LexisNexis API call here. Return a list of "
        "{name, phone, email, mailing_address, confidence} dicts."
    )


_DISPATCH = {
    "tlo": _trace_tlo,
    "batchskiptracing": _trace_batchskiptracing,
    "idi": _trace_idi,
}


def skip_trace_lead(lead_id: int) -> list[dict]:
    """Trace one lead and persist any contacts found. Raises if not configured."""
    provider, key = _require_provider()
    lead = repo.get_lead(lead_id)
    if not lead:
        raise SkipTraceError(f"Lead {lead_id} not found")

    results = _DISPATCH[provider](lead, key)  # raises NotImplementedError until wired
    for r in results:
        repo.add_contact(
            lead_id,
            name=r.get("name"),
            phone=r.get("phone"),
            email=r.get("email"),
            mailing_address=r.get("mailing_address"),
            provider=provider,
            confidence=r.get("confidence"),
        )
    return results
