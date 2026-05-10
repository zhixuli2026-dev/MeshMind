"""Unit tests for core business logic."""
from datetime import timedelta, datetime, timezone

from meshmind.core.lifecycle import (
    compute_current_vitality,
    compute_new_half_life,
    get_initial_half_life,
    get_initial_vitality,
    get_max_half_life,
    is_below_threshold,
)


def test_initial_half_life_by_type():
    assert get_initial_half_life("law").days == 365 * 5
    assert get_initial_half_life("event").days == 5
    assert get_initial_half_life("unknown").days == 60  # fallback


def test_initial_vitality():
    assert get_initial_vitality("manual") == 1.2
    assert get_initial_vitality("conversation") == 1.0


def test_current_vitality_no_decay():
    v = compute_current_vitality(
        last_vitality=1.0,
        half_life=timedelta(days=365),
        last_event_time=datetime.now(timezone.utc),
    )
    assert v == 1.0


def test_current_vitality_one_half_life():
    now = datetime.now(timezone.utc)
    past = now - timedelta(days=365)
    v = compute_current_vitality(
        last_vitality=1.0,
        half_life=timedelta(days=365),
        last_event_time=past,
        now=now,
    )
    assert abs(v - 0.5) < 0.01


def test_current_vitality_two_half_lives():
    now = datetime.now(timezone.utc)
    past = now - timedelta(days=730)
    v = compute_current_vitality(
        last_vitality=1.0,
        half_life=timedelta(days=365),
        last_event_time=past,
        now=now,
    )
    assert abs(v - 0.25) < 0.01


def test_below_threshold():
    assert is_below_threshold(0.05) is True
    assert is_below_threshold(0.5) is False


def test_positive_feedback_increases_half_life():
    current = timedelta(days=60)  # best_practice initial
    new = compute_new_half_life(current, "best_practice")
    assert new > current
    # Should not exceed max
    assert new <= get_max_half_life("best_practice")
