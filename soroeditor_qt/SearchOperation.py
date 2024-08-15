from dataclasses import dataclass


@dataclass
class Match:
    start: int
    end: int
    group: str
    box: int
