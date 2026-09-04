from dataclasses import dataclass


@dataclass
class RawJob:
    source: str
    source_type: str
    raw_data: dict