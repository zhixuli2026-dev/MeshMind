import math
from datetime import datetime, timedelta, timezone

from meshmind.core.config import settings

# Initial half-life values per knowledge type (in days for storage convenience)
INITIAL_HALF_LIFE_DAYS = {
    "law": 365 * 5,          # 5 years
    "rule": int(365 * 1.5),  # 1.5 years
    "best_practice": 60,     # 2 months
    "event": 5,              # 5 days
}

MAX_HALF_LIFE_DAYS = {
    "law": 365 * 10,         # 10 years
    "rule": 365 * 3,         # 3 years
    "best_practice": 180,    # 6 months
    "event": 15,             # 15 days
}

INITIAL_VITALITY = 1.0
MANUAL_INPUT_VITALITY_BOOST = 1.2
VITALITY_THRESHOLD = 0.1
POSITIVE_FEEDBACK_RATE = 0.001  # 0.1% increase per positive feedback


def get_initial_half_life(knowledge_type: str) -> timedelta:
    days = INITIAL_HALF_LIFE_DAYS.get(knowledge_type, 60)
    return timedelta(days=days)


def get_max_half_life(knowledge_type: str) -> timedelta:
    days = MAX_HALF_LIFE_DAYS.get(knowledge_type, 180)
    return timedelta(days=days)


def get_initial_vitality(source_type: str) -> float:
    if source_type == "manual":
        return MANUAL_INPUT_VITALITY_BOOST
    return INITIAL_VITALITY


def compute_current_vitality(
    last_vitality: float,
    half_life: timedelta,
    last_event_time: datetime,
    now: datetime | None = None,
) -> float:
    if now is None:
        now = datetime.now(timezone.utc)
    age = (now - last_event_time).total_seconds()
    hl_seconds = half_life.total_seconds()
    if hl_seconds <= 0:
        return last_vitality
    return last_vitality * math.pow(0.5, age / hl_seconds)


def compute_new_half_life(current_half_life: timedelta, knowledge_type: str) -> timedelta:
    max_hl = get_max_half_life(knowledge_type)
    increase = current_half_life.total_seconds() * POSITIVE_FEEDBACK_RATE
    new_seconds = min(
        current_half_life.total_seconds() + increase,
        max_hl.total_seconds(),
    )
    return timedelta(seconds=new_seconds)


def is_below_threshold(vitality: float) -> bool:
    return vitality < VITALITY_THRESHOLD
