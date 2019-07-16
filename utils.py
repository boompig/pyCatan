'''Commonly used utilities.'''


from functools import reduce


class CatanUtils():
    @staticmethod
    def print_dict(d):
        for k, v in d.items():
            print("{} ==> {}".format(k, v))

    @staticmethod
    def get_tkinter_coords(normal_person_coords):
        '''Works on lists, too.
        :param normal_person_coords: List of coordinates.
        :returns: Coordinates in TKinter'''

        return reduce(tuple.__add__, normal_person_coords)

    @staticmethod
    def get_num_token_dots(num: int) -> int:
        '''Return the number of dots on the token with given number'''

        return 6 - abs(7 - num)
