
jsontree - build, parse and explore json data
=======================================================

*Travis integration TBD*

jsontree is a simple module for quickly building manipulating and modifying
rich json data in python.

Datetime objects are serialized out ti the ISO format which is easilly used
in javascript. ISO formatted datetime strings will be deserialized into
datetime objects. 

.. code::

    import jsontree
    import datetime
    data = jsontree.jsontree()
    data.username = 'doug'
    data.meta.date = datetime.datetime.now()
    data.somethingelse = [1,2,3]

    data['username'] == 'doug'
    
    ser = jsontree.dumps(data)
    backagain = jsontree.loads(ser)
    cloned = jsontree.clone(data)
    
    