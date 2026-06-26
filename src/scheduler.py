import json
from datetime import datetime
from pathlib import Path

SCHEDULES_PATH = Path(__file__).parent.parent / "schedules.json"

DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

# chat_id → имя менеджера (для двух аккаунтов заменить на разные chat_id)
MANAGER_NAMES: dict[int, str] = {
    1386279071: "Oskar",
}


def get_on_duty_manager() -> tuple[int, str]:
    with open(SCHEDULES_PATH, encoding="utf-8") as f:
        schedules = json.load(f)

    now = datetime.now()
    day = DAYS[now.weekday()]
    hour = now.hour

    day_schedule = schedules.get(day, {})
    for time_range, chat_id in day_schedule.items():
        start, end = map(int, time_range.split("-"))
        if start <= hour < end:
            name = MANAGER_NAMES.get(chat_id, f"Manager {chat_id}")
            return chat_id, name

    first_chat_id = next(iter(day_schedule.values()))
    name = MANAGER_NAMES.get(first_chat_id, f"Manager {first_chat_id}")
    return first_chat_id, name
