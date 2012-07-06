import collections
import json

__version__ = '0.1'
__author__ = 'Doug Napoleone'
__email__ = 'doug.napoleone@gmail.com'

class jsontree(collections.defaultdict):
    """TBD
    """
    def __init__(self, *args, **kwdargs):
        super(jsontree, self).__init__(jsontree, *args, **kwdargs)
        
    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return self[name]
    
    def __setattr__(self, name, value):
        self[name] = value
        return value

def decoder(dictobj):
    """TBD
    """
    return jsontree(dictobj)

def clone(root):
    """TBD
    """
    return json.loads(json.dumps(root, object_hook=jsontree_decoder))
    
def dump(*args, **kargs):
    """TBD
    """
    return json.dump(*args, **kargs)

def dumps(*args, **kargs):
    """TBD
    """
    return json.dumps(*args, **kargs)

def load(fp, encoding=None, cls=None, object_hook=None,
         parse_float=None, parse_int=None, parse_constant=None,
         object_pairs_hook=None, **kargs):
    """TBD
    """
    if object_hook is None:
        object_hook = decoder
    return json.load(fp, encoding, cls, object_hook,
         parse_float, parse_int, parse_constant,
         object_pairs_hook, **kargs)
    
def loads(s, encoding=None, cls=None, object_hook=None,
         parse_float=None, parse_int=None, parse_constant=None,
         object_pairs_hook=None, **kargs):
    """TBD
    """
    if object_hook is None:
        object_hook = decoder
    return json.load(s, encoding, cls, object_hook,
         parse_float, parse_int, parse_constant,
         object_pairs_hook, **kargs)
