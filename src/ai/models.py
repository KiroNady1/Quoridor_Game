from dataclasses import dataclass
from typing import TypeAlias

Position: TypeAlias = tuple[int, int]
Score: TypeAlias = float


@dataclass(frozen=True)
class EvalWeights:
    distance: int
    walls: int
    mobility: int


@dataclass(frozen=True)
class AIConfig:
    depth: int
    weights: EvalWeights
    use_astar: bool
