from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class MissionRecord:
    mission_id: str
    started_at: datetime
    status: str
    duration_seconds: int
    result: str

