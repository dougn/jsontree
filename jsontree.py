"""JSON Tree Library

"""
import collections
import datetime
import json
import json.scanner
import re

__version__ = [0,1,0]
__version_string__ = '.'.join(str(x) for x in __version__)

__author__ = 'Doug Napoleone'
__email__ = 'doug.napoleone+jsontree@gmail.com'

# ISO date example: 2013-04-29T22:45:35.294303
_datetime_iso_re = re.compile(
    r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,7})?Z?')

# Future: support UTC formatted datetime string from javascript libraries
_datetime_utc_re = re.compile(
    r'^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$')

class jsontree(collections.defaultdict):
    """Default dictionary where keys can be accessed as attributes and
    new entries recursively default to be this class. This means the following
    code is valid:
    
    >>> mytree = jsontree()
    >>> mytree.something.else=3
    >>> mytree['something']['else'] == 3
    True
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

class JSONTreeEncoder(json.JSONEncoder):
    """JSON encoder class that serializes out jsontree object structures and
    datetime objects into ISO strings.
    """
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        else:
            return super(JSONTreeEncoder, self).default(obj)

class JSONTreeDecoder(json.JSONDecoder):
    """JSON decoder class for deserializing to a jsontree object structure
    and building datetime objects from strings with the ISO datetime format.
    """
    def __init__(self, *args, **kwdargs):
        super(JSONTreeDecoder, self).__init__(*args, **kwdargs)
        self.__parse_object = self.parse_object
        self.__parse_string = self.parse_string
        self.parse_object = self._parse_object
        self.parse_string = self._parse_string
        self.scan_once = json.scanner.py_make_scanner(self)
    def _parse_object(self, *args, **kwdargs):
        result = self.__parse_object(*args, **kwdargs)
        return jsontree(result[0]), result[1]
    def _parse_string(self, *args, **kwdargs):
        value, idx = self.__parse_string(*args, **kwdargs)
        if _datetime_iso_re.match(value):
            try:
                if value.endswith('Z'):
                    result = datetime.datetime.strptime(
                        value, "%Y-%m-%dT%H:%M:%S.%fZ")
                else:
                    result = datetime.datetime.strptime(
                        value, "%Y-%m-%dT%H:%M:%S.%f")
                return result, idx
            except ValueError:
                return value, idx
        return value, idx

def clone(root):
    """Clone an object by first searializing out and then loading it back in.
    """
    return json.loads(json.dumps(root, cls=JSONTreeEncoder),
                      cls=JSONTreeDecoder)
    
def dump(obj, fp, skipkeys=False, ensure_ascii=True, check_circular=True,
         allow_nan=True, cls=JSONTreeEncoder, indent=None, separators=None,
         encoding="utf-8", default=None, sort_keys=False, **kw):
    """JSON serialize to file function that defaults the encoding class to be
    JSONTreeEncoder
    """
    return json.dump(obj, fp, skipkeys, ensure_ascii, check_circular,
                     allow_nan, cls, indent, separators, encoding, default,
                     sort_keys, **kw)

def dumps(obj, skipkeys=False, ensure_ascii=True, check_circular=True,
          allow_nan=True, cls=JSONTreeEncoder, indent=None, separators=None,
          encoding="utf-8", default=None, sort_keys=False, **kw):
    """JSON serialize to string function that defaults the encoding class to be
    JSONTreeEncoder
    """
    return json.dumps(obj, skipkeys, ensure_ascii, check_circular, allow_nan,
                      cls, indent, separators, encoding, default, sort_keys,
                      **kw)

def load(fp, encoding=None, cls=JSONTreeDecoder, object_hook=None,
         parse_float=None, parse_int=None, parse_constant=None,
         object_pairs_hook=None, **kargs):
    """JSON load from file function that defaults the loading class to be
    JSONTreeDecoder
    """
    return json.load(fp, encoding, cls, object_hook,
         parse_float, parse_int, parse_constant,
         object_pairs_hook, **kargs)
    
def loads(s, encoding=None, cls=JSONTreeDecoder, object_hook=None,
         parse_float=None, parse_int=None, parse_constant=None,
         object_pairs_hook=None, **kargs):
    """JSON load from string function that defaults the loading class to be
    JSONTreeDecoder
    """
    return json.load(s, encoding, cls, object_hook,
         parse_float, parse_int, parse_constant,
         object_pairs_hook, **kargs)
