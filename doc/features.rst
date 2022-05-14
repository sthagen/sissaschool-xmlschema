**************
Other features
**************

Schema objects and package APIs include a set of other features that have been
added since a specific release. These features are regulated by arguments,
alternative classes or module parameters.


XSD 1.0 and 1.1 support
=======================

From release v1.0.14 XSD 1.1 support has been added to the library through the class
:class:`XMLSchema11`. You have to use this class for XSD 1.1 schemas instead the default
class :class:`XMLSchema`, that is linked to XSD 1.0 validator :class:`XMLSchema10`.

The XSD 1.1 validator can be used also for validating XSD 1.0 schemas, except for a
restricted set of cases related to content extension in a complexType (the extension
of a complex content with simple base is allowed in XSD 1.0 and forbidden in XSD 1.1).


CLI interface
=============

Starting from the version v1.2.0 the package has a CLI interface with three console scripts:

xmlschema-validate
    Validate a set of XML files.

xmlschema-xml2json
    Decode a set of XML files to JSON.

xmlschema-json2xml
    Encode a set of JSON files to XML.


XSD validation modes
====================

Since the version v0.9.10 the library uses XSD validation modes *strict*/*lax*/*skip*,
both for schemas and for XML instances. Each validation mode defines a specific behaviour:

strict
    Schemas are validated against the meta-schema. The processor stops when an error is
    found in a schema or during the validation/decode of XML data.

lax
    Schemas are validated against the meta-schema. The processor collects the errors
    and continues, eventually replacing missing parts with wildcards.
    Undecodable XML data are replaced with `None`.

skip
    Schemas are not validated against the meta-schema. The processor doesn't collect
    any error. Undecodable XML data are replaced with the original text.

The default mode is *strict*, both for schemas and for XML data. The mode is set with
the *validation* argument, provided when creating the schema instance or when you want to
validate/decode XML data.
For example you can build a schema using a *strict* mode and then decode XML data
using the *validation* argument setted to 'lax'.

.. note::
    From release v1.1.1 the *iter_decode()* and *iter_encode()* methods propagate
    errors also for *skip* validation mode. The errors generated in *skip* mode are
    discarded by the top-level methods *decode()* and *encode()*.


Lazy validation
===============

From release v1.0.12 the document validation and the decoding API have an optional argument
`lazy=False`, that can be changed to `True` for operating with a lazy :class:`XMLResource`.
The lazy mode can be useful for validating and decoding big XML data files, consuming
less memory.

From release v1.1.0 the *lazy* mode can be also set with a non negative integer.
A zero is equivalent to `False`, a positive value means that lazy mode is activated
and defines also the *lazy depth* to use for traversing the XML data tree.

Lazy mode works better with validation because is not needed to use converters for
shaping decoded data.


XML entity-based attacks protection
===================================

The XML data resource loading is protected using the  `SafeXMLParser` class, a subclass
of the pure Python version of XMLParser that forbids the use of entities.
The protection is applied both to XSD schemas and to XML data. The usage of this feature
is regulated by the XMLSchema's argument *defuse*.

For default this argument has value *'remote'* that means the protection on XML data is
applied only to data loaded from remote. Providing *'nonlocal'* all XML data are defused
except local files. Other values for this argument can be *'always'* and *'never'*, with
obvious meaning.


Access control on accessing resources
=====================================

From release v1.2.0 the schema class includes an argument named *allow* for
protecting the access to XML resources identified by an URL or filesystem path.
For default all types of URLs are allowed. Provide a different value to restrict
the set of URLs that the schema instance can access:

all
    All types of URL and file paths are allowed.

remote
    Only remote resource URLs are allowed.

local
    Only file paths and file-related URLs are allowed.

sandbox
    Allows only the file paths and URLs that are under the directory path
    identified by *source* argument or *base_url* argument.

none
    No URL based or file path access is allowed.


.. warning::
    For protecting services that are freely accessible for validation (eg. a web
    on-line validator that has a form for loading schema and/or XML instance) the
    recommendation is to provide 'always' for the *defuse* argument and 'none' for
    the *allow* argument. These settings prevent attacks to your local filesystem,
    through direct paths or injection in XSD schema imports or includes.

    For XSD schemas, if you want to permit imports of namespaces located on other
    web services you can provide 'remote' for the *allow* argument and provide an
    `XMLResource` instance, initialized providing `allow='none'`, as the *source*
    argument for the main schema.


Processing limits
=================

From release v1.0.16 a module has been added in order to group constants that define
processing limits, generally to protect against attacks prepared to exhaust system
resources. These limits usually don't need to be changed, but this possibility has
been left at the module level for situations where a different setting is needed.


Limit on XSD model groups checking
----------------------------------

Model groups of the schemas are checked against restriction violations and *Unique Particle
Attribution* violations. To avoids XSD model recursion attacks a depth limit of 15 levels
is set. If this limit is exceeded an ``XMLSchemaModelDepthError`` is raised, the error is
caught and a warning is generated. If you need to set an higher limit for checking all your
groups you can import the library and change the value of ``MAX_MODEL_DEPTH`` in the limits
module:

.. doctest::

    >>> import xmlschema
    >>> xmlschema.limits.MAX_MODEL_DEPTH = 20


Limit on XML data depth
-----------------------

A limit of 9999 on maximum depth is set for XML validation/decoding/encoding to avoid
attacks based on extremely deep XML data. To increase or decrease this limit change the
value of ``MAX_XML_DEPTH`` in the module *limits* after the import of the package:

.. doctest::

    >>> import xmlschema
    >>> xmlschema.limits.MAX_XML_DEPTH = 1000


Translations of parsing/validation error messages
=================================================

From release v1.11.0 translation of parsing/validation error messages can
be activated:

.. doctest::

    >>> import xmlschema
    >>> xmlschema.translation.activate()

.. note::
    Activation depends by the default language in your environment and if it matches
    translations provided with the library. You can build your custom translation from
    the template included in the repository (`xmlschema/locale/xmlschema.pot`) and then
    use it in your runs providing *localedir* and *languages* arguments to activation call.
    See :ref:`translation-api` for information.

Translations for default do not interfere with other translations installed
at runtime and can be deactivated after:

.. doctest::

    >>> xmlschema.translation.deactivate()

