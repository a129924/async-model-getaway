"""RED coverage for the internal response-cache freshness-policy contract."""

from __future__ import annotations

import inspect
from datetime import datetime
from typing import get_type_hints

from async_model_gateway.response_cache.freshness_policy import FreshnessPolicy


def test_freshness_policy_exposes_only_keyword_timestamp_freshness_contract() -> None:
    """The internal policy contract must stay limited to one boolean decision."""
    signature = inspect.signature(FreshnessPolicy.is_fresh)

    assert tuple(signature.parameters) == ("self", "written_at", "now")
    assert signature.parameters["written_at"].kind is inspect.Parameter.KEYWORD_ONLY
    assert signature.parameters["now"].kind is inspect.Parameter.KEYWORD_ONLY
    assert get_type_hints(FreshnessPolicy.is_fresh) == {
        "written_at": datetime,
        "now": datetime,
        "return": bool,
    }
    assert not hasattr(FreshnessPolicy, "is_expired")
