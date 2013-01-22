
'''Commonly used utilities.'''
    
class CatanUtils():
    @staticmethod
    def print_dict(d):
        for k, v in d.iteritems():
            print "{} ==> {}".format(k, v)
            
    @staticmethod
    def get_tkinter_coords(normal_person_coords):
        '''Works on lists, too.'''
        
        return reduce(tuple.__add__, normal_person_coords)