from game_engine import Game
from catan_types import Vertex, Edge, HexCoord
from typing import Optional, List, Tuple


class AI:
    def __init__(self, color: str, game: Game) -> None:
        # raise NotImplementedError("implement in subclass")
        pass

    def get_settlement_placement(self, game: Game) -> Vertex:
        raise NotImplementedError("implement in subclass")

    def get_road_placement(self, game: Game, settlement_placement: Vertex) -> Edge:
        raise NotImplementedError("implement in subclass")

    def do_turn(self, game: Game) -> None:
        raise NotImplementedError("implement in subclass")

    def robber_discard(self, game: Game) -> List[str]:
        raise NotImplementedError("implement in subclass")

    def get_robber_placement(self, game: Game) -> Tuple[Optional[str], HexCoord]:
        raise NotImplementedError("implement in subclass")
