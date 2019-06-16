"""JSON Tree Library

"""
import collections
import datetime
import json
import json.scanner
import re
import sys

__version__ = (0,5,1)
__version_string__ = '.'.join(str(x) for x in __version__)

__author__ = 'Doug Napoleone'
__email__ = 'doug.napoleone+jsontree@gmail.com'


if sys.version_info.major > 2 :
    basestring = str

# ISO/UTC date examples:
#    2013-04-29T22:45:35.294303Z
#    2013-04-29T22:45:35.294303
#    2013-04-29 22:45:35
#    2013-04-29T22:45:35.4361-0400
#    2013-04-29T22:45:35.4361-04:00
_datetime_iso_re = re.compile(
    r'^(?P<parsable>\d{4}-\d{2}-\d{2}(?P<T>[ T])\d{2}:\d{2}:\d{2}'
    r'(?P<f>\.\d{1,7})?)(?P<z>[-+]\d{2}\:?\d{2})?(?P<Z>Z)?')

_date = "%Y-%m-%d"
_time = "%H:%M:%S"
_f = '.%f'
_z = '%z'

class _FixedTzOffset(datetime.tzinfo):
    def __init__(self, offset_str):
        hours = int(offset_str[1:3], 10)
        mins = int(offset_str[-2:], 10)
        if offset_str[0] == '-':
            hours = -hours
            mins = -mins
        self.__offset = datetime.timedelta(hours=hours,
                                           minutes=mins)
        self.__dst = datetime.timedelta(hours=hours-1,
                                        minutes=mins)
        self.__name = ''

    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return self.__name

    def dst(self, dt):
        return self.__dst

def _datetimedecoder(dtstr):
    match = _datetime_iso_re.match(dtstr)
    if match:
        gd = match.groupdict()
        T = gd['T']
        strptime = _date + T + _time
        if gd['f']:
            strptime += '.%f'
        if gd['Z']:
            strptime += 'Z'
        try:
            result = datetime.datetime.strptime(gd['parsable'], strptime)
            if gd['z']:
                result = result.replace(tzinfo=_FixedTzOffset(gd['z']))
            return result
        except ValueError:
            return dtstr
    return dtstr

def _datetimeencoder(dtobj):
    return dtobj.isoformat()
    
class jsontree(collections.defaultdict):
    """Default dictionary where keys can be accessed as attributes and
    new entries recursively default to be this class. This means the following
    code is valid:
    
    >>> mytree = jsontree()
    >>> mytree.something.there = 3
    >>> mytree['something']['there'] == 3
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

def mapped_jsontree_class(mapping):
    """Return a class which is a jsontree, but with a supplied attribute name
    mapping. The mapping argument can be a mapping object
    (dict, jsontree, etc.) or it can be a callable which takes a single
    argument (the attribute name), and returns a new name.
    
    This is useful in situations where you have a jsontree with keys that are
    not valid python attribute names, to simplify communication with a client
    library, or allow for configurable names.
    
    For example:
    
    >>> numjt = mapped_jsontree_class(dict(one='1', two='2', three='3'))
    >>> number = numjt()
    >>> number.one = 'something'
    >>> dict(number)
    {'1': 'something'}
    
    This is very useful for abstracting field names that may change between
    a development sandbox and production environment. Both FogBugz and Jira
    bug trackers have custom fields with dynamically generated values. These
    field names can be abstracted out into a configruation mapping, and the
    jsontree code can be standardized.
    
    This can also be iseful for JavaScript API's (PHPCake) which insist on
    having spaces in some key names. A function can be supplied which maps
    all '_'s in the attribute name to spaces:
    
    >>> spacify = lambda name: name.replace('_', ' ')
    >>> spacemapped = mapped_jsontree_class(spacify)
    >>> sm = spacemapped()
    >>> sm.hello_there = 5
    >>> sm.hello_there
    5
    >>> list(sm.keys())
    ['hello there']
    
        
    This will also work with non-string keys for translating from libraries
    that use object keys in python over to string versions of the keys in JSON
    
    >>> numjt = mapped_jsontree_class(dict(one=1, two=2))
    >>> number = numjt()
    >>> number.one = 'something'
    >>> dict(number)
    {1: 'something'}
    >>> numjt_as_text = mapped_jsontree_class(dict(one='1', two='2'))
    >>> dumped_number = dumps(number)
    >>> loaded_number = loads(dumped_number, jsontreecls=numjt_as_text)
    >>> str(loaded_number.one)
    'something'
    >>> repr(dict(loaded_number)).replace('u', '') # cheat the python2 tests
    "{'1': 'something'}"
    
    """
    mapper = mapping
    if not callable(mapping):
        if not isinstance(mapping, collections.Mapping):
            raise TypeError("Argument mapping is not collable or an instance "
                              "of collections.Mapping")
        mapper = lambda name: mapping.get(name, name)
    class mapped_jsontree(collections.defaultdict):
        def __init__(self, *args, **kwdargs):
            super(mapped_jsontree, self).__init__(mapped_jsontree, *args, **kwdargs)
        def __getattribute__(self, name):
            mapped_name = mapper(name)
            if not isinstance(mapped_name, basestring):
                return self[mapped_name]
            try:
                return object.__getattribute__(self, mapped_name)
            except AttributeError:
                return self[mapped_name]
        def __setattr__(self, name, value):
            mapped_name = mapper(name)
            self[mapped_name] = value
            return value
    return mapped_jsontree

def mapped_jsontree(mapping, *args, **kwdargs):
    """Helper function that calls mapped_jsontree_class, and passing the
    rest of the arguments to the constructor of the new class.
    
    >>> number = mapped_jsontree(dict(one='1', two='2', three='3', four='4'),
    ...                          {'1': 'something', '2': 'hello'})
    >>> number.two
    'hello'
    >>> list(number.items())
    [('1', 'something'), ('2', 'hello')]
    
    """
    return mapped_jsontree_class(mapping)(*args, **kwdargs)
    
class JSONTreeEncoder(json.JSONEncoder):
    """JSON encoder class that serializes out jsontree object structures and
    datetime objects into ISO strings.
    """
    def __init__(self, *args, **kwdargs):
        datetimeencoder = _datetimeencoder
        if 'datetimeencoder' in kwdargs:
            datetimeencoder = kwdargs.pop('datetimeencoder')
        super(JSONTreeEncoder, self).__init__(*args, **kwdargs)
        self.__datetimeencoder = datetimeencoder
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return self.__datetimeencoder(obj)
        else:
            return super(JSONTreeEncoder, self).default(obj)

class JSONTreeDecoder(json.JSONDecoder):
    """JSON decoder class for deserializing to a jsontree object structure
    and building datetime objects from strings with the ISO datetime format.
    """
    def __init__(self, *args, **kwdargs):
        jsontreecls = jsontree
        datetimedecoder = _datetimedecoder
        if 'jsontreecls' in kwdargs:
            jsontreecls = kwdargs.pop('jsontreecls')
        if 'datetimedecoder' in kwdargs:
            datetimedecoder = kwdargs.pop('datetimedecoder')
        super(JSONTreeDecoder, self).__init__(*args, **kwdargs)
        self.__parse_object = self.parse_object
        self.__parse_string = self.parse_string
        self.parse_object = self._parse_object
        self.parse_string = self._parse_string
        self.scan_once = json.scanner.py_make_scanner(self)
        self.__jsontreecls = jsontreecls
        self.__datetimedecoder = datetimedecoder
    def _parse_object(self, *args, **kwdargs):
        result = self.__parse_object(*args, **kwdargs)
        return self.__jsontreecls(result[0]), result[1]
    def _parse_string(self, *args, **kwdargs):
        value, idx = self.__parse_string(*args, **kwdargs)
        value = self.__datetimedecoder(value)
        return value, idx

def clone(root, jsontreecls=jsontree, datetimeencoder=_datetimeencoder,
          datetimedecoder=_datetimedecoder):
    """Clone an object by first searializing out and then loading it back in.
    """
    return json.loads(json.dumps(root, cls=JSONTreeEncoder,
                                 datetimeencoder=datetimeencoder),
                      cls=JSONTreeDecoder, jsontreecls=jsontreecls,
                      datetimedecoder=datetimedecoder)
    
def dump(obj, fp, skipkeys=False, ensure_ascii=True, check_circular=True,
         allow_nan=True, cls=JSONTreeEncoder, indent=None, separators=None,
         encoding="utf-8", default=None, sort_keys=False, **kargs):
    """JSON serialize to file function that defaults the encoding class to be
    JSONTreeEncoder
    """
    if sys.version_info.major == 2:
        kargs['encoding'] = encoding
    if sys.version_info.major > 2 :
        kargs['sort_keys'] = sort_keys
    kargs['default'] = default
    return json.dump(obj, fp, skipkeys=skipkeys, ensure_ascii=ensure_ascii, 
                     check_circular=check_circular, allow_nan=allow_nan,
                     cls=cls, indent=indent, separators=separators, **kargs)

def dumps(obj, skipkeys=False, ensure_ascii=True, check_circular=True,
          allow_nan=True, cls=JSONTreeEncoder, indent=None, separators=None,
          encoding='utf-8', default=None, sort_keys=False, **kargs):
    """JSON serialize to string function that defaults the encoding class to be
    JSONTreeEncoder
    """

    if sys.version_info.major == 2:
        kargs['encoding'] = encoding
    if sys.version_info.major > 2 :
        kargs['sort_keys'] = sort_keys
    kargs['default'] = default
    return json.dumps(obj, skipkeys=skipkeys, ensure_ascii=ensure_ascii, 
                      check_circular=check_circular, allow_nan=allow_nan,
                      cls=cls, indent=indent, separators=separators, **kargs)

def load(fp, encoding=None, cls=JSONTreeDecoder, object_hook=None,
         parse_float=None, parse_int=None, parse_constant=None,
         object_pairs_hook=None, **kargs):
    """JSON load from file function that defaults the loading class to be
    JSONTreeDecoder
    """
    if sys.version_info.major == 2:
        kargs['encoding'] = encoding
    return json.load(fp, cls=cls, object_hook=object_hook,
         parse_float=parse_float, parse_int=parse_int, parse_constant=parse_constant,
         object_pairs_hook=object_pairs_hook, **kargs)
    
def loads(s, encoding=None, cls=JSONTreeDecoder, object_hook=None,
         parse_float=None, parse_int=None, parse_constant=None,
         object_pairs_hook=None, **kargs):
    """JSON load from string function that defaults the loading class to be
    JSONTreeDecoder
    """
    return json.loads(s, encoding=encoding, cls=cls, object_hook=object_hook,
         parse_float=parse_float, parse_int=parse_int, parse_constant=parse_constant,
         object_pairs_hook=object_pairs_hook, **kargs)
