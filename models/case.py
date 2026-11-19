from dataclasses import dataclass

@dataclass
class Case:
    data: dict

    @classmethod
    def from_dict(cls, data):
        return cls(data)

    def to_dict(self):
        return dict(self.data)
