from game_engine import Game
from catan_types import Vertex, Edge
from typing import Optional, List


class AI:
    def get_settlement_placement(self, game: Game) -> Vertex:
        raise NotImplementedError("implement in subclass")

    def get_road_placement(self, game: Game, settlement_placement: Vertex) -> Edge:
        raise NotImplementedError("implement in subclass")

    def do_turn(self, game: Game) -> None:
        raise NotImplementedError("implement in subclass")

    def robber_discard(self, game: Game, color: str) -> List[str]:
        raise NotImplementedError("implement in subclass")
