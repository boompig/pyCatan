'''Commonly used utilities.'''


from functools import reduce
from typing import Tuple, Union


class CatanUtils():
    @staticmethod
    def print_dict(d):
        for k, v in d.items():
            print("{} ==> {}".format(k, v))

    @staticmethod
    def get_tkinter_coords(normal_person_coords: Union[Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int], Tuple[int, int], Tuple[int, int], Tuple[int, int]], Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int], Tuple[int, int]]]) -> Union[Tuple[int, int, int, int, int, int, int, int], Tuple[int, int, int, int, int, int, int, int, int, int, int, int]]:
        '''Works on lists, too.'''

        return reduce(tuple.__add__, normal_person_coords)

    @staticmethod
    def get_num_token_dots(num: int) -> int:
        '''Return the number of dots on the token with given number'''

        return 6 - abs(7 - num)
