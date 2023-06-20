import enum


class StrEnum(str, enum.Enum):
    def __repr__(self) -> str:
        return str.__repr__(self.value)

    def __str__(self) -> str:
        return self.value
