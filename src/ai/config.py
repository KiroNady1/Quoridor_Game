from enum import Enum
from ai.models import AIConfig, EvalWeights


class Mode(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


CONFIGS = {
    Mode.EASY: AIConfig(
        depth=2,
        weights=EvalWeights(
            distance=3,
            walls=1,
            mobility=1,
        ),
        use_astar=False,
    ),
    Mode.MEDIUM: AIConfig(
        depth=3,
        weights=EvalWeights(
            distance=10,
            walls=1,
            mobility=10,
        ),
        use_astar=False,
    ),
    Mode.HARD: AIConfig(
        depth=7,
        weights=EvalWeights(
            distance=15,
            walls=10,
            mobility=5,
        ),
        use_astar=True,
    ),
}


def get_config(mode: Mode) -> AIConfig:
    return CONFIGS[mode]
