.. _package-api:

***********
Package API
***********

API includes classes and methods imported at package level and others included in
subpackages. Only the modules, classes and methods imported within the top-level
package are in fact to be considered as public API.

.. _errors-and-exceptions:

Errors and exceptions
=====================

.. autoexception:: xmlschema.XMLSchemaException
.. autoexception:: xmlschema.XMLResourceError
.. autoexception:: xmlschema.XMLSchemaNamespaceError

.. autoexception:: xmlschema.XMLSchemaValidatorError
.. autoexception:: xmlschema.XMLSchemaNotBuiltError
.. autoexception:: xmlschema.XMLSchemaParseError
.. autoexception:: xmlschema.XMLSchemaModelError
.. autoexception:: xmlschema.XMLSchemaModelDepthError
.. autoexception:: xmlschema.XMLSchemaValidationError
.. autoexception:: xmlschema.XMLSchemaDecodeError
.. autoexception:: xmlschema.XMLSchemaEncodeError
.. autoexception:: xmlschema.XMLSchemaChildrenValidationError

    .. autoattribute:: invalid_tag
    .. autoattribute:: invalid_child

.. autoexception:: xmlschema.XMLSchemaStopValidation
.. autoexception:: xmlschema.XMLSchemaIncludeWarning
.. autoexception:: xmlschema.XMLSchemaImportWarning
.. autoexception:: xmlschema.XMLSchemaTypeTableWarning


.. _document-level-api:

Document level API
==================

.. autofunction:: xmlschema.validate
.. autofunction:: xmlschema.is_valid
.. autofunction:: xmlschema.iter_errors
.. autofunction:: xmlschema.iter_decode
.. autofunction:: xmlschema.to_dict
.. autofunction:: xmlschema.to_json
.. autofunction:: xmlschema.to_etree
.. autofunction:: xmlschema.from_json


.. _schema-level-api:

Schema level API
================

.. autoclass:: xmlschema.XMLSchema10
.. autoclass:: xmlschema.XMLSchema11

    The classes for XSD v1.0 and v1.1 schema instances. They are both generated by the
    meta-class :class:`XMLSchemaMeta` and take the same API of :class:`xmlschema.XMLSchemaBase`.

.. autoclass:: xmlschema.XMLSchema

.. autoclass:: xmlschema.validators.XMLSchemaMeta
.. autoclass:: xmlschema.XMLSchemaBase

    .. autoattribute:: meta_schema
    .. autoattribute:: builders

    .. autoattribute:: root
    .. automethod:: get_text
    .. autoattribute:: name
    .. autoattribute:: url
    .. autoattribute:: base_url

    .. autoattribute:: tag
    .. autoattribute:: id
    .. autoattribute:: version

    .. autoattribute:: schema_location
    .. autoattribute:: no_namespace_schema_location
    .. autoattribute:: target_prefix
    .. autoattribute:: default_namespace
    .. autoattribute:: root_elements
    .. autoattribute:: simple_types
    .. autoattribute:: complex_types

    .. automethod:: builtin_types
    .. automethod:: create_meta_schema

    .. automethod:: get_locations
    .. automethod:: include_schema
    .. automethod:: import_schema
    .. automethod:: add_schema
    .. automethod:: export
    .. automethod:: resolve_qname
    .. automethod:: iter_globals
    .. automethod:: iter_components

    .. automethod:: build
    .. automethod:: clear
    .. autoattribute:: built
    .. autoattribute:: validation_attempted
    .. autoattribute:: validity
    .. autoattribute:: all_errors

    .. automethod:: get_converter
    .. automethod:: validate
    .. automethod:: is_valid
    .. automethod:: iter_errors

    .. automethod:: decode
    .. automethod:: iter_decode

    .. automethod:: encode
    .. automethod:: iter_encode


.. _global-maps-api:

Global maps API
===============

.. autoclass:: xmlschema.XsdGlobals
    :members: copy, register, iter_schemas, iter_globals, lookup,
        clear, build, unbuilt, check


.. _converters-api:

Converters API
==============

The base class `XMLSchemaConverter` is used for defining generic converters.
The subclasses implement some of the most used `conventions for converting XML
to JSON data <http://wiki.open311.org/JSON_and_XML_Conversion/>`_.

.. autoclass:: xmlschema.ElementData

.. autoclass:: xmlschema.XMLSchemaConverter

    .. autoattribute:: lossy
    .. autoattribute:: losslessly

    .. automethod:: copy
    .. automethod:: map_attributes
    .. automethod:: map_content
    .. automethod:: etree_element
    .. automethod:: element_decode
    .. automethod:: element_encode

    .. automethod:: map_qname
    .. automethod:: unmap_qname

.. autoclass:: xmlschema.UnorderedConverter

.. autoclass:: xmlschema.ParkerConverter

.. autoclass:: xmlschema.BadgerFishConverter

.. autoclass:: xmlschema.AbderaConverter

.. autoclass:: xmlschema.JsonMLConverter

.. autoclass:: xmlschema.ColumnarConverter


.. _data-objects-api:

Data objects API
================

.. autoclass:: xmlschema.DataElement
.. autoclass:: xmlschema.DataElementConverter
.. autoclass:: xmlschema.DataBindingConverter


.. _url-normalization-api:

URL normalization API
=====================

.. autofunction:: xmlschema.normalize_url
.. autofunction:: xmlschema.normalize_locations


.. _xml-resource-api:

XML resources API
=================

.. autofunction:: xmlschema.fetch_resource
.. autofunction:: xmlschema.fetch_schema_locations
.. autofunction:: xmlschema.fetch_schema
.. autofunction:: xmlschema.download_schemas

.. autoclass:: xmlschema.XMLResource

    .. autoattribute:: root
    .. autoattribute:: text
    .. autoattribute:: name
    .. autoattribute:: url
    .. autoattribute:: base_url
    .. autoattribute:: filepath
    .. autoattribute:: namespace

    .. automethod:: parse
    .. automethod:: tostring
    .. automethod:: open
    .. automethod:: load
    .. automethod:: is_lazy
    .. autoattribute:: lazy_depth
    .. automethod:: is_remote
    .. automethod:: is_local
    .. automethod:: is_loaded
    .. automethod:: iter
    .. automethod:: iter_depth
    .. automethod:: iterfind
    .. automethod:: find
    .. automethod:: findall
    .. automethod:: iter_location_hints
    .. automethod:: get_namespaces
    .. automethod:: get_locations

.. autoclass:: xmlschema.XmlDocument


.. _loaders-api:

Loaders API
===========

.. autofunction:: xmlschema.SchemaLoader
.. autofunction:: xmlschema.LocationSchemaLoader
.. autofunction:: xmlschema.SafeSchemaLoader


.. _translation-api:

Translation API
===============

.. autofunction:: xmlschema.translation.activate
.. autofunction:: xmlschema.translation.deactivate


.. _namespace-api:

Namespaces API
==============

Classes for converting namespace representation or for accessing namespace objects:

.. autoclass:: xmlschema.namespaces.NamespaceResourcesMap
.. autoclass:: xmlschema.namespaces.NamespaceMapper
.. autoclass:: xmlschema.namespaces.NamespaceView


.. _xpath-api:

XPath API
=========

Implemented through a mixin class on XSD schemas and elements.

.. autoclass:: xmlschema.ElementPathMixin

    .. autoattribute:: tag
    .. autoattribute:: attrib
    .. automethod:: get
    .. automethod:: iter
    .. automethod:: iterchildren
    .. automethod:: find
    .. automethod:: findall
    .. automethod:: iterfind


.. autoclass:: xmlschema.ElementSelector

    .. autoattribute:: path
    .. autoattribute:: namespaces
    .. autoattribute:: parts
    .. autoattribute:: relative_path
    .. autoattribute:: depth
    .. autoattribute:: select_all
    .. automethod:: select
    .. automethod:: iter_select
    .. automethod:: cached_selector

.. autoclass:: xmlschema.ElementPathSelector


.. _validation-api:

Validation API
==============

Implemented for XSD schemas, elements, attributes, types, attribute
groups and model groups.

.. autoclass:: xmlschema.validators.ValidationMixin

    .. automethod:: is_valid
    .. automethod:: validate
    .. automethod:: decode
    .. automethod:: iter_decode
    .. automethod:: iter_encode
        :noindex:
    .. automethod:: iter_errors
    .. automethod:: encode
    .. automethod:: iter_encode


.. _particles-api:

Particles API
=============

Implemented for XSD model groups, elements and element wildcards.

.. autoclass:: xmlschema.validators.ParticleMixin

    .. automethod:: is_empty
    .. automethod:: is_emptiable
    .. automethod:: is_single
    .. automethod:: is_multiple
    .. automethod:: is_ambiguous
    .. automethod:: is_univocal
    .. automethod:: is_missing
    .. automethod:: is_over


.. _main-xsd-components:

Main XSD components
===================

.. autoclass:: xmlschema.XsdComponent

    .. autoattribute:: target_namespace
    .. autoattribute:: qualified
    .. autoattribute:: local_name
    .. autoattribute:: qualified_name
    .. autoattribute:: prefixed_name
    .. automethod:: is_global
    .. automethod:: is_matching
    .. automethod:: tostring


.. autoclass:: xmlschema.XsdType
    :members: is_simple, is_complex, is_atomic, is_primitive, is_list, is_union,
        is_empty, is_emptiable, has_simple_content, has_complex_content, has_mixed_content,
        is_element_only, is_derived, is_extension, is_restriction, is_blocked,
        is_dynamic_consistent, is_key, is_qname, is_notation, is_datetime, is_decimal,
        is_boolean, overall_min_occurs, overall_max_occurs

    .. autoattribute:: content_type_label
    .. autoattribute:: sequence_type
    .. autoattribute:: root_type
    .. autoattribute:: simple_type
    .. autoattribute:: model_group


.. autoclass:: xmlschema.XsdElement
    :members: get_binding, get_path, match_child, overall_min_occurs, overall_max_occurs

    .. autoattribute:: type
    .. autoattribute:: attributes
    .. autoattribute:: min_occurs
    .. autoattribute:: max_occurs
    .. autoattribute:: abstract
    .. autoattribute:: block
    .. autoattribute:: final
    .. autoattribute:: default
    .. autoattribute:: fixed
    .. autoattribute:: qualified


.. autoclass:: xmlschema.XsdAttribute

    .. autoattribute:: type
    .. autoattribute:: default
    .. autoattribute:: fixed
    .. autoattribute:: use
    .. autoattribute:: inheritable
    .. autoattribute:: qualified


.. _other-xsd-components:

Other XSD components
====================

Elements and attributes
-----------------------
.. autoclass:: xmlschema.validators.Xsd11Element
.. autoclass:: xmlschema.validators.Xsd11Attribute


Types
-----
.. autoclass:: xmlschema.validators.Xsd11ComplexType
.. autoclass:: xmlschema.validators.XsdComplexType

    .. autoattribute:: content

.. autoclass:: xmlschema.validators.XsdSimpleType

    .. autoattribute:: enumeration
    .. autoattribute:: max_value
    .. autoattribute:: min_value

.. autoclass:: xmlschema.validators.XsdAtomicBuiltin
.. autoclass:: xmlschema.validators.XsdList
.. autoclass:: xmlschema.validators.Xsd11Union
.. autoclass:: xmlschema.validators.XsdUnion
.. autoclass:: xmlschema.validators.Xsd11AtomicRestriction
.. autoclass:: xmlschema.validators.XsdAtomicRestriction


Attribute and model groups
--------------------------
.. autoclass:: xmlschema.validators.XsdAttributeGroup
.. autoclass:: xmlschema.validators.Xsd11Group
.. autoclass:: xmlschema.validators.XsdGroup


Wildcards
---------
.. autoclass:: xmlschema.validators.Xsd11AnyElement
.. autoclass:: xmlschema.validators.XsdAnyElement
.. autoclass:: xmlschema.validators.Xsd11AnyAttribute
.. autoclass:: xmlschema.validators.XsdAnyAttribute
.. autoclass:: xmlschema.validators.XsdOpenContent
.. autoclass:: xmlschema.validators.XsdDefaultOpenContent


Identity constraints
--------------------
.. autoclass:: xmlschema.validators.XsdIdentity
.. autoclass:: xmlschema.validators.XsdSelector
.. autoclass:: xmlschema.validators.XsdFieldSelector
.. autoclass:: xmlschema.validators.Xsd11Unique
.. autoclass:: xmlschema.validators.XsdUnique
.. autoclass:: xmlschema.validators.Xsd11Key
.. autoclass:: xmlschema.validators.XsdKey
.. autoclass:: xmlschema.validators.Xsd11Keyref
.. autoclass:: xmlschema.validators.XsdKeyref


Facets
------
.. autoclass:: xmlschema.validators.XsdFacet
.. autoclass:: xmlschema.validators.XsdWhiteSpaceFacet
.. autoclass:: xmlschema.validators.XsdLengthFacet
.. autoclass:: xmlschema.validators.XsdMinLengthFacet
.. autoclass:: xmlschema.validators.XsdMaxLengthFacet
.. autoclass:: xmlschema.validators.XsdMinInclusiveFacet
.. autoclass:: xmlschema.validators.XsdMinExclusiveFacet
.. autoclass:: xmlschema.validators.XsdMaxInclusiveFacet
.. autoclass:: xmlschema.validators.XsdMaxExclusiveFacet
.. autoclass:: xmlschema.validators.XsdTotalDigitsFacet
.. autoclass:: xmlschema.validators.XsdFractionDigitsFacet
.. autoclass:: xmlschema.validators.XsdExplicitTimezoneFacet
.. autoclass:: xmlschema.validators.XsdAssertionFacet
.. autoclass:: xmlschema.validators.XsdEnumerationFacets
.. autoclass:: xmlschema.validators.XsdPatternFacets


Others
------
.. autoclass:: xmlschema.validators.XsdAssert
.. autoclass:: xmlschema.validators.XsdAlternative
.. autoclass:: xmlschema.validators.XsdNotation
.. autoclass:: xmlschema.validators.XsdAnnotation


.. _extra-api:

Extra features API
==================

Code generators
---------------

.. autoclass:: xmlschema.extras.codegen.AbstractGenerator

    .. automethod:: map_type
    .. automethod:: list_templates
    .. automethod:: matching_templates
    .. automethod:: get_template
    .. automethod:: select_template
    .. automethod:: render
    .. automethod:: render_to_files


.. autoclass:: xmlschema.extras.codegen.PythonGenerator


WSDL 1.1 documents
------------------

.. autoclass:: xmlschema.extras.wsdl.Wsdl11Document

    .. autoattribute:: messages
    .. autoattribute:: port_types
    .. autoattribute:: bindings
    .. autoattribute:: services
