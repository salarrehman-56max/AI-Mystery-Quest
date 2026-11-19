from dataclasses import dataclass, field

@dataclass
class Player:
    score: int = 100
    collected_evidence: list = field(default_factory=list)
    hints_used: int = 0
    completed_cases: int = 0
