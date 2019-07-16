import random
from hex import Hex
from map_gen import MapGen
from typing import Tuple, Dict, List, Optional
from catan_types import Vertex, Edge


class AI():

    def __init__(self, board: MapGen) -> None:
        self._board = board
        self._vertex_probs = {}  # type: Dict[int, List[Vertex]]

    def prepare(self) -> None:
        '''Prepare the AI by letting it calculate most probable settlements.'''

        self._vertex_probs = {}

        for v in self._board.get_nodes():
            n = self._eval_vertex_value(v)

            if n not in self._vertex_probs:
                self._vertex_probs[n] = []
            self._vertex_probs[n].append(v)

    def _eval_vertex_value(self, v: Tuple[int, int]) -> int:
        '''Evaluate the value of the given vertex.
        This is done by adding all the dots of the adjacent hexes.
        This is a rough measure of probability.'''

        n = 0

        for hex in self._board._vertex_map[v]:
            n += hex.get_num_dots()

        return n

    def get_random_road_from_settlement(self, v: Vertex) -> Optional[Edge]:
        '''Return a random road stemming from settlement located at v.'''

        adjacent_v_set = self._board.get_adjacent_vertices(v)
        random.shuffle(adjacent_v_set)

        for v2 in adjacent_v_set:
            if not self._board.has_road(v, v2):
               return (v, v2) # the road was built

        return None # no road can be built from this settlement

    def _eval_hex_robber_score(self, hex: Hex, color: str) -> int:
        '''Return the robber score for this hex.
        Hex gets a point value of 0 if `color` is on it.
        Neutral hexes get a point-value of 1 for tie-break.
        Also 0 is the previous robber hex.'''

        score = 1 # neutral hexes get 1 point

        if hex == self._board.get_robber_hex():
            return 0

        for v in hex.get_vertices():
            if v in self._board._settlements:
                s = self._board._settlements[v]

                if s.color() == color:
                    return 0 # no points for hexes with same color as choosing player
                elif s.is_city():
                    score += 2 * hex.get_num_dots()
                else :
                    score += 1 * hex.get_num_dots()

        return score

    def get_random_robber_pick(self) -> str:
        '''Return a color to steal from. This is random.'''

        l = []

        for v in self._board.get_robber_hex().get_vertices():
            if v in self._board._settlements:
                l.append(self._board._settlements[v].color())

        return random.choice(l)

    def get_smart_robber_placement(self, color: str) -> Vertex:
        '''Return the *position* of the hex on which to place the robber.
        Should be a high-producing hex with no settlements/cities by this player.
        Color is the color of the player placing the robber.'''

        max_score = 0
        best_hex = None

        for row_i, row in enumerate(self._board._board):
            for col, hex in enumerate(row):
                score = self._eval_hex_robber_score(hex, color)
                if score > max_score:
                    #best_hex = hex
                    best_hex = (row_i, col)
                    max_score = score
        assert best_hex is not None
        return best_hex

    def get_best_settlement(self) -> Optional[Vertex]:
        '''Return the settlement with the highest combined prob. of generating a resource.'''

        sorted_vals = list(self._vertex_probs.keys())
        assert sorted_vals != []
        sorted_vals.sort(reverse=True)
        s = self._board.available_settlement_set

        # this has to go through all of them...
        for val in sorted_vals:
            for v in self._vertex_probs[val]:
                if v in s:
                    return v
            # all of these are now off the table
            del(self._vertex_probs[val])
        return None

    def get_random_settlement(self):
        '''Return a valid settlement placement.'''

        # randomly pick a valid vertex to place a settlement
        v = random.choice(list(self._board.available_settlement_set))
        return v

    def get_random_road(self, color):
        '''Return a valid road placement for the given player.
        This placement is chosen at random.'''

        # pick a random settlement to start the road from
        player = self._board.get_player(color)
        nexi = [player.get_settlement(i) for i in range(player.get_num_settlements())]
        random.shuffle(nexi)

        # if I made
        while len(nexi) > 0:
            s = nexi.pop()
            v1 = s.vertex()

            # TODO replace with get_random_road_from_settlement

            for v2 in self._board.get_adjacent_vertices(v1):
                if not self._board.has_road(v1, v2):
                   return (v1, v2) # the road was built

        # cycled through all possible settlement-road combinations and could not find valid placement
        return False

    def get_random_discard(self, color, num_discard):
        '''Discard random cards from the player's hand.
        Return those cards.'''

        player = self._board.get_player(color)
        hand = player.get_hand()[:]
        gone_list = []

        for i in range(num_discard):
            gone_list.append(hand.pop())

        player.deduct_resources(gone_list)
        return gone_list


