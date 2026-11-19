from dataclasses import dataclass

@dataclass
class Suspect:
    name: str
    role: str
    background: str
    motive: str
    alibi: str
