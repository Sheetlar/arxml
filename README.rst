AUTOSAR
-------

Python  `AUTOSAR <https://www.autosar.org/>`_ XML parser.

AUTOSAR version support
-----------------------

* AUTOSAR 3.0
* AUTOSAR 4.2

Requirements
------------

* `Python 3.11 <https://www.python.org/>`_

Documentation
-------------

To parse ARXML file, use ``parse_arxml`` function
from ``autosar.extractor.parse_arxml``

Provide it with ``pathlib.Path`` to ARXML file you want to parse.
You will receive a tuple of ``ExtractedSystem`` elements.

``ExtractedSystem`` object consist of:

* ``System`` that was extracted
* A tuple of FIBEX elements the system defines
* SOME/IP service ID, method ID and interface version mapping to name/structure tuple
* Source IP address and port to ECU mapping
