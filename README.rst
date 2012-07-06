=======================================================
 jsontree -- 
=======================================================

.. note:: Travis integration TBD

jsontree is a simple module for quickly building manipulating and modifying
rich json data in python.

Documentation
=============

TBD

.. code-block:: python

    import jsontree
    data = jsontree.jsontree()
    data.username = 'doug'
    data.meta.date = '2012-07-06'
    data.somethingelse = []
    
    ser = jsontree.dumps(data)
    backagain = jsontree.loads(ser)
    cloned = jsontree.clone(data)
    
    