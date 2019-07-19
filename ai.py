from game_engine import Game
from catan_types import Vertex, Edge
from typing import Optional, List


class AI:
    def get_settlement_placement(self, game: Game) -> Vertex:
        raise NotImplementedError("implement in subclass")

    def get_road_placement(self, game: Game, settlement_placement: Vertex) -> Edge:
        raise NotImplementedError("implement in subclass")

    def get_structure_to_buy(self, game: Game) -> Optional[dict]:
        raise NotImplementedError("implement in subclass")

    def get_robber_discard(self, game: Game, color: str, num_discard: int) -> List[str]:
        raise NotImplementedError("implement in subclass")
