#!/usr/bin/env python
#
# Copyright (c), 2016-2020, SISSA (International School for Advanced Studies).
# All rights reserved.
# This file is distributed under the terms of the MIT License.
# See the file 'LICENSE' in the root directory of the present
# distribution, or http://opensource.org/licenses/MIT.
#
# @author Davide Brunato <brunato@sissa.it>
#
import sys
import unittest
import logging
import warnings
import pathlib
import pickle
import os
from textwrap import dedent
from xml.etree.ElementTree import Element

import xmlschema
from xmlschema import XMLSchemaParseError, XMLSchemaIncludeWarning, XMLSchemaImportWarning
from xmlschema.names import XML_NAMESPACE, XSD_ELEMENT, XSI_TYPE
from xmlschema.locations import SCHEMAS_DIR
from xmlschema.loaders import SchemaLoader
from xmlschema.validators import XMLSchemaBase, XMLSchema10, XMLSchema11, \
    XsdGlobals, XsdComponent
from xmlschema.testing import SKIP_REMOTE_TESTS, XsdValidatorTestCase
from xmlschema.validators.schemas import logger
from xmlschema.validators.builders import XsdBuilders
from xmlschema.validators import XMLSchemaValidationError, XsdComplexType, \
    XsdAttributeGroup, XsdElement, XsdGroup


class CustomXMLSchema(XMLSchema10):
    pass


class TestXMLSchema10(XsdValidatorTestCase):
    cases_dir = pathlib.Path(__file__).parent.parent.joinpath('test_cases')
    maxDiff = None

    class CustomXMLSchema(XMLSchema10):
        pass

    def test_schema_subclasses(self):
        self.assertIs(CustomXMLSchema.meta_schema, XMLSchema10.meta_schema)
        self.assertIs(self.CustomXMLSchema.meta_schema, self.schema_class.meta_schema)

    def test_schema_validation(self):
        schema = self.schema_class(self.vh_xsd_file)
        self.assertEqual(schema.validation, 'strict')

        schema = self.schema_class(self.vh_xsd_file, validation='lax')
        self.assertEqual(schema.validation, 'lax')

        schema = self.schema_class(self.vh_xsd_file, validation='skip')
        self.assertEqual(schema.validation, 'skip')

        with self.assertRaises(ValueError):
            self.schema_class(self.vh_xsd_file, validation='none')

    def test_schema_string_repr(self):
        schema = self.schema_class(self.vh_xsd_file)
        tmpl = "%s(name='vehicles.xsd', namespace='http://example.com/vehicles')"
        self.assertEqual(str(schema), tmpl % self.schema_class.__name__)

    def test_schema_copy(self):
        schema = self.vh_schema.copy()
        self.assertNotEqual(id(self.vh_schema), id(schema))
        self.assertNotEqual(id(self.vh_schema.namespaces), id(schema.namespaces))

        # The map is not automatically changed
        self.assertEqual(id(self.vh_schema.maps), id(schema.maps))

    def test_schema_location_hints(self):
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            schema = self.schema_class(dedent("""\
                <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
                    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                    xsi:schemaLocation="http://xmlschema.test/ns schema.xsd">
                  <xs:element name="root" />
                </xs:schema>"""))

        self.assertEqual(schema.schema_location, [("http://xmlschema.test/ns", "schema.xsd")])
        self.assertIsNone(schema.no_namespace_schema_location)

        schema = self.schema_class(dedent("""\
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xsi:noNamespaceSchemaLocation="schema.xsd">
              <xs:element name="root" />
            </xs:schema>"""))

        self.assertEqual(schema.schema_location, [])
        self.assertEqual(schema.no_namespace_schema_location, 'schema.xsd')

    def test_target_prefix(self):
        schema = self.schema_class(dedent("""\
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
                targetNamespace="http://xmlschema.test/ns">
              <xs:element name="root" />
            </xs:schema>"""))

        self.assertEqual(schema.target_prefix, '')

        schema = self.schema_class(dedent("""\
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
                xmlns:tns="http://xmlschema.test/ns"
                targetNamespace="http://xmlschema.test/ns">
              <xs:element name="root" />
            </xs:schema>"""))

        self.assertEqual(schema.target_prefix, 'tns')

    def test_builtin_types(self):
        self.assertIn('string', self.schema_class.builtin_types())

        with self.assertRaises(RuntimeError):
            self.schema_class.meta_schema.builtin_types()

    def test_resolve_qname(self):
        schema = self.schema_class(dedent("""\
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
              <xs:element name="root" />
            </xs:schema>"""))

        self.assertEqual(schema.resolve_qname('xs:element'), XSD_ELEMENT)
        self.assertEqual(schema.resolve_qname('xsi:type'), XSI_TYPE)

        self.assertEqual(schema.resolve_qname(XSI_TYPE), XSI_TYPE)
        self.assertEqual(schema.resolve_qname('element'), 'element')
        self.assertRaises(ValueError, schema.resolve_qname, '')
        self.assertRaises(ValueError, schema.resolve_qname, 'xsi:a type ')
        self.assertRaises(ValueError, schema.resolve_qname, 'xml::lang')

    def test_global_group_definitions(self):
        schema = self.check_schema("""
            <xs:group name="wrong_child">
              <xs:element name="foo"/>
            </xs:group>""", validation='lax')

        self.assertEqual(len(schema.errors), 1)
        self.assertEqual(len(schema.all_errors), 2)  # error in xs:group
        self.assertEqual(schema.total_errors, 2)

        self.check_schema('<xs:group name="empty" />', XMLSchemaParseError)
        self.check_schema('<xs:group name="empty"><xs:annotation/></xs:group>', XMLSchemaParseError)

    def test_wrong_includes_and_imports(self):

        with warnings.catch_warnings(record=True) as context:
            warnings.simplefilter("always")
            self.check_schema("""
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" targetNamespace="ns">
                <xs:include schemaLocation="example.xsd" />
                <xs:import schemaLocation="example.xsd" />
                <xs:redefine schemaLocation="example.xsd"/>
                <xs:import namespace="http://missing.example.test/" />
                <xs:import/>
            </xs:schema>
            """)
            self.assertEqual(len(context), 3, "Wrong number of include/import warnings")
            self.assertEqual(context[0].category, XMLSchemaIncludeWarning)
            self.assertEqual(context[1].category, XMLSchemaImportWarning)
            self.assertEqual(context[2].category, XMLSchemaIncludeWarning)
            self.assertTrue(str(context[0].message).startswith("Include"))
            self.assertTrue(str(context[1].message).startswith("Import of namespace"))
            self.assertTrue(str(context[2].message).startswith("Redefine"))

    def test_import_mismatch_with_locations__issue_324(self):
        xsd1_path = self.casepath('../test_cases/features/namespaces/import-case5a.xsd')
        xsd2_path = self.casepath('../test_cases/features/namespaces/import-case5b.xsd')
        xsd3_path = self.casepath('../test_cases/features/namespaces/import-case5c.xsd')

        schema = self.schema_class(xsd1_path, locations=[
            ('http://xmlschema.test/other-ns', xsd2_path),
            ('http://xmlschema.test/other-ns2', xsd3_path),
        ])
        self.assertTrue(schema.built)

        with self.assertRaises(xmlschema.XMLSchemaParseError):
            self.schema_class(xsd1_path, locations=[
                ('http://xmlschema.test/wrong-ns', xsd2_path),
                ('http://xmlschema.test/wrong-ns2', xsd3_path),
            ])

    def test_wrong_references(self):
        # Wrong namespace for element type's reference
        self.check_schema("""
        <xs:element name="dimension" type="xs:dimensionType"/>
        <xs:simpleType name="dimensionType">
          <xs:restriction base="xs:short"/>
        </xs:simpleType>
        """, XMLSchemaParseError)

    def test_annotations(self):
        schema = self.check_schema("""
            <xs:element name='foo'>
                <xs:annotation />
            </xs:element>""")
        xsd_element = schema.elements['foo']
        self.assertIsNotNone(xsd_element.annotation)

        self.check_schema("""
        <xs:simpleType name='Magic'>
            <xs:annotation />
            <xs:annotation />
            <xs:restriction base='xs:string'>
                <xs:enumeration value='A'/>
            </xs:restriction>
        </xs:simpleType>""", XMLSchemaParseError)

        schema = self.check_schema("""
        <xs:simpleType name='Magic'>
            <xs:annotation>
                <xs:documentation> stuff </xs:documentation>
            </xs:annotation>
            <xs:restriction base='xs:string'>
                <xs:enumeration value='A'/>
            </xs:restriction>
        </xs:simpleType>""")

        xsd_type = schema.types["Magic"]
        self.assertEqual(str(xsd_type.annotation), ' stuff ')

    def test_components(self):
        components = self.col_schema.components
        self.assertIsInstance(components, dict)
        self.assertEqual(len(components), 25)

        for elem, component in components.items():
            self.assertIsInstance(component, XsdComponent)
            self.assertIs(elem, component.elem)

    def test_annotation_string(self):
        schema = self.check_schema("""
            <xs:element name='A'>
                <xs:annotation>
                    <xs:documentation>A element info</xs:documentation>
                </xs:annotation>
            </xs:element>
            <xs:element name='B'>
                <xs:annotation>
                    <xs:documentation>B element extended info, line1</xs:documentation>
                    <xs:documentation>B element extended info, line2</xs:documentation>
                </xs:annotation>
            </xs:element>""")

        xsd_element = schema.elements['A']
        self.assertEqual(str(xsd_element.annotation), 'A element info')
        self.assertEqual(repr(xsd_element.annotation), "XsdAnnotation('A element info')")

        xsd_element = schema.elements['B']
        self.assertEqual(str(xsd_element.annotation),
                         'B element extended info, line1\nB element extended info, line2')
        self.assertEqual(repr(xsd_element.annotation),
                         "XsdAnnotation('B element extended info, line1\\nB element')")

    def test_schema_annotations(self):
        schema = self.schema_class(dedent("""\
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
                <xs:element name="root"/>
            </xs:schema>"""))

        self.assertListEqual(schema.annotations, [])
        annotations = schema.annotations
        self.assertListEqual(annotations, [])
        self.assertIs(annotations, schema.annotations)

        schema = self.schema_class(dedent("""\
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
                <xs:annotation>
                    <xs:documentation>First annotation</xs:documentation>
                </xs:annotation>
                <xs:annotation>
                    <xs:documentation>Second annotation</xs:documentation>
                </xs:annotation>
                <xs:element name="root"/>
                <xs:annotation>
                    <xs:documentation>Third annotation</xs:documentation>
                </xs:annotation>
            </xs:schema>"""))

        schema.clear()
        annotations = schema.annotations
        self.assertEqual(len(annotations), 3)
        self.assertEqual(repr(annotations[0]), "XsdAnnotation('First annotation')")
        self.assertEqual(repr(annotations[1]), "XsdAnnotation('Second annotation')")
        self.assertEqual(repr(annotations[2]), "XsdAnnotation('Third annotation')")
        self.assertIs(annotations, schema.annotations)

    def test_base_schemas(self):
        xsd_file = os.path.join(SCHEMAS_DIR, 'XML/xml.xsd')
        schema = self.schema_class(xsd_file)
        self.assertEqual(schema.target_namespace, XML_NAMESPACE)

    def test_root_elements(self):
        schema = self.schema_class(dedent("""\
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"/>"""))
        self.assertEqual(schema.root_elements, [])

        schema = self.schema_class(dedent("""\
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
              <xs:element name="root" />
            </xs:schema>"""))
        self.assertEqual(schema.root_elements, [schema.elements['root']])

        # Test issue #107 fix
        schema = self.schema_class(dedent("""\
            <?xml version="1.0" encoding="utf-8"?>
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
                <xs:element name="root1" type="root"/>
                <xs:element name="root2" type="root"/>
                <xs:complexType name="root">
                    <xs:sequence>
                        <xs:element name="elementWithNoType"/>
                    </xs:sequence>
                </xs:complexType>
            </xs:schema>"""))

        self.assertEqual(set(schema.root_elements),
                         {schema.elements['root1'], schema.elements['root2']})

    def test_simple_types(self):
        self.assertListEqual(self.vh_schema.simple_types, [])
        self.assertGreater(len(self.st_schema.simple_types), 20)

    def test_complex_types(self):
        self.assertListEqual(self.vh_schema.complex_types,
                             [self.vh_schema.types['vehicleType']])

    def test_is_restriction_method(self):
        # Test issue #111 fix
        schema = self.schema_class(source=self.casepath('issues/issue_111/issue_111.xsd'))
        extended_header_def = schema.types['extendedHeaderDef']
        self.assertTrue(extended_header_def.is_derived(schema.types['blockDef']))

    @unittest.skipIf(SKIP_REMOTE_TESTS, "Remote networks are not accessible.")
    def test_remote_schemas_loading(self):
        col_schema = self.schema_class("https://raw.githubusercontent.com/brunato/xmlschema/master/"
                                       "tests/test_cases/examples/collection/collection.xsd",
                                       timeout=300)
        self.assertTrue(isinstance(col_schema, self.schema_class))
        vh_schema = self.schema_class("https://raw.githubusercontent.com/brunato/xmlschema/master/"
                                      "tests/test_cases/examples/vehicles/vehicles.xsd",
                                      timeout=300)
        self.assertTrue(isinstance(vh_schema, self.schema_class))

    def test_schema_defuse(self):
        vh_schema = self.schema_class(self.vh_xsd_file, defuse='always')
        self.assertIsInstance(vh_schema.root, Element)
        for schema in vh_schema.maps.iter_schemas():
            self.assertIsInstance(schema.root, Element)

    def test_logging(self):
        self.schema_class(self.vh_xsd_file, loglevel=logging.ERROR)
        self.assertEqual(logger.level, logging.WARNING)

        with self.assertLogs('xmlschema', level='INFO') as ctx:
            self.schema_class(self.vh_xsd_file, loglevel=logging.INFO)

        self.assertEqual(logger.level, logging.WARNING)
        self.assertEqual(len(ctx.output), 7)
        self.assertIn("INFO:xmlschema:Process xs:include schema from ", ctx.output[0])

        with self.assertLogs('xmlschema', level='DEBUG') as ctx:
            self.schema_class(self.vh_xsd_file, loglevel=logging.DEBUG)

        self.assertEqual(logger.level, logging.WARNING)
        self.assertEqual(len(ctx.output), 32)
        self.assertIn("DEBUG:xmlschema:Schema targetNamespace is "
                      "'http://example.com/vehicles'", ctx.output)

        # With string argument
        with self.assertRaises(ValueError) as ctx:
            self.schema_class(self.vh_xsd_file, loglevel='all')
        self.assertEqual(str(ctx.exception), "'all' is not a valid loglevel")

        with self.assertLogs('xmlschema', level='INFO') as ctx:
            self.schema_class(self.vh_xsd_file, loglevel='INFO')
        self.assertEqual(len(ctx.output), 7)

        with self.assertLogs('xmlschema', level='INFO') as ctx:
            self.schema_class(self.vh_xsd_file, loglevel='  Info ')
        self.assertEqual(len(ctx.output), 7)

    def test_target_namespace(self):
        schema = self.schema_class(dedent("""\
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
                    targetNamespace="http://xmlschema.test/ns">
                <xs:element name="root"/>
            </xs:schema>"""))
        self.assertEqual(schema.target_namespace, 'http://xmlschema.test/ns')

        schema = self.schema_class(dedent("""\
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
                <xs:element name="root"/>
            </xs:schema>"""))
        self.assertEqual(schema.target_namespace, '')

        with self.assertRaises(XMLSchemaParseError) as ctx:
            self.schema_class(dedent("""\
                <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
                        targetNamespace="">
                    <xs:element name="root"/>
                </xs:schema>"""))

        self.assertEqual(ctx.exception.message,
                         "the attribute 'targetNamespace' cannot be an empty string")

    def test_block_default(self):
        schema = self.schema_class(dedent("""\
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
                    blockDefault="extension restriction ">
                <xs:element name="root"/>
            </xs:schema>"""))
        self.assertEqual(schema.block_default, 'extension restriction ')

        schema = self.schema_class(dedent("""\
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
                    blockDefault="#all">
                <xs:element name="root"/>
            </xs:schema>"""))
        self.assertEqual(set(schema.block_default.split()),
                         {'substitution', 'extension', 'restriction'})

        with self.assertRaises(XMLSchemaParseError) as ctx:
            self.schema_class(dedent("""\
                <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
                        blockDefault="all">>
                    <xs:element name="root"/>
                </xs:schema>"""))

        self.assertEqual(ctx.exception.message,
                         "wrong value 'all' for attribute 'blockDefault'")

        with self.assertRaises(XMLSchemaParseError) as ctx:
            self.schema_class(dedent("""\
                <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
                        blockDefault="#all restriction">>
                    <xs:element name="root"/>
                </xs:schema>"""))

        self.assertEqual(ctx.exception.message,
                         "wrong value '#all restriction' for attribute 'blockDefault'")

    def test_final_default(self):
        schema = self.schema_class(dedent("""\
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
                    finalDefault="extension restriction ">
                <xs:element name="root"/>
            </xs:schema>"""))
        self.assertEqual(schema.final_default, 'extension restriction ')

        schema = self.schema_class(dedent("""\
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
                    finalDefault="#all">
                <xs:element name="root"/>
            </xs:schema>"""))
        self.assertEqual(set(schema.final_default.split()),
                         {'list', 'union', 'extension', 'restriction'})

        with self.assertRaises(XMLSchemaParseError) as ctx:
            self.schema_class(dedent("""\
                <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
                        finalDefault="all">>
                    <xs:element name="root"/>
                </xs:schema>"""))

        self.assertEqual(ctx.exception.message,
                         "wrong value 'all' for attribute 'finalDefault'")

    def test_use_fallback(self):
        source = dedent("""\
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
                <xs:element name="root"/>
            </xs:schema>""")

        schema = self.schema_class(source)
        self.assertEqual(schema.maps.loader.fallback_locations,
                         SchemaLoader.fallback_locations)
        schema = self.schema_class(source, use_fallback=False)
        self.assertEqual(schema.maps.loader.fallback_locations, {})

    def test_global_maps(self):
        source = dedent("""\
                    <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
                        <xs:element name="root"/>
                    </xs:schema>""")
        col_schema = self.schema_class(self.col_xsd_file)

        with self.assertRaises(TypeError) as ctx:
            self.schema_class(self.col_schema, global_maps=col_schema)  # noqa
        self.assertIn(" for argument 'source'", str(ctx.exception))

        schema = self.schema_class(source, global_maps=col_schema.maps)
        self.assertIs(col_schema.maps, schema.maps)

    def test_version_control(self):
        schema = self.schema_class(dedent("""
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
                <xs:element name="root">
                    <xs:complexType>
                        <xs:attribute name="a" use="required"/>
                        <xs:assert test="@a > 300" vc:minVersion="1.1"
                            xmlns:vc="http://www.w3.org/2007/XMLSchema-versioning"/>
                    </xs:complexType>
                </xs:element>
            </xs:schema>"""))
        self.assertEqual(len(schema.root[0][0]), 1 if schema.XSD_VERSION == '1.0' else 2)

        schema = self.schema_class(dedent("""
            <xs:schema vc:minVersion="1.1" elementFormDefault="qualified"
                    xmlns:xs="http://www.w3.org/2001/XMLSchema"
                    xmlns:vc="http://www.w3.org/2007/XMLSchema-versioning">
                <xs:element name="root"/>
            </xs:schema>"""))
        self.assertEqual(len(schema.root), 0 if schema.XSD_VERSION == '1.0' else 1)

    def test_xsd_version_compatibility_property(self):
        self.assertEqual(self.vh_schema.xsd_version, self.vh_schema.XSD_VERSION)

    def test_explicit_locations(self):
        source = dedent("""\
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
                <xs:element name="root"/>
            </xs:schema>""")

        locations = {'http://example.com/vehicles': self.vh_xsd_file}
        schema = self.schema_class(source, locations=locations)
        self.assertEqual(len(schema.maps.namespaces['http://example.com/vehicles']), 4)

    def test_use_meta_property(self):
        self.assertTrue(self.vh_schema.use_meta)
        self.assertTrue(self.col_schema.use_meta)

        schema = self.schema_class(dedent("""\
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
                <xs:element name="foo"/>
            </xs:schema>"""), use_meta=False)
        self.assertIs(self.schema_class.meta_schema, schema.meta_schema)
        self.assertFalse(schema.use_meta)

    def test_other_schema_root_attributes(self):
        self.assertIsNone(self.vh_schema.id)
        self.assertIsNone(self.vh_schema.version)

        schema = self.schema_class(dedent("""\
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" id="foo" version="2.0">
                <xs:element name="foo"/>
            </xs:schema>"""))
        self.assertEqual(schema.id, 'foo')
        self.assertEqual(schema.version, '2.0')

    def test_change_maps_attribute(self):
        schema = self.schema_class(dedent("""\
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
                <xs:element name="root"/>
            </xs:schema>"""))
        self.assertTrue(schema.built)

        with self.assertRaises(AttributeError) as ctx:
            schema.meta_schema.maps = XsdGlobals(schema.copy())
        self.assertEqual(str(ctx.exception),
                         "can't change the global maps instance of a class meta-schema")

        with self.assertRaises(AttributeError) as ctx:
            XsdGlobals(schema)
        self.assertEqual(str(ctx.exception),
                         "can't change the global maps instance of a schema that "
                         "is the main validator of another global maps instance")

        self.assertTrue(schema.built)
        schema = schema.copy()
        maps, schema.maps = schema.maps, XsdGlobals(schema)
        self.assertIsNot(maps, schema.maps)
        self.assertFalse(schema.built)

        schema = schema.copy()
        with self.assertRaises(ValueError) as ctx:
            schema.maps = maps
        self.assertIn("is already registered", str(ctx.exception))

    def test_listed_and_reversed_elements(self):
        schema = self.schema_class(dedent("""\
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
                <xs:element name="elem1"/>
                <xs:element name="elem2"/>
                <xs:element name="elem3"/>
            </xs:schema>"""))

        elements = list(schema)
        self.assertListEqual(elements, [schema.elements['elem1'],
                                        schema.elements['elem2'],
                                        schema.elements['elem3']])
        elements.reverse()
        self.assertListEqual(elements, list(reversed(schema)))

    def test_multi_schema_initialization(self):
        source1 = dedent("""\
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
                <xs:element name="elem1"/>
            </xs:schema>""")

        source2 = dedent("""\
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
                <xs:element name="elem2"/>
            </xs:schema>""")

        source3 = dedent("""\
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
                <xs:element name="elem3"/>
            </xs:schema>""")

        schema = self.schema_class([source1, source2, source3])
        self.assertEqual(len(schema.elements), 3)
        self.assertEqual(len(schema.maps.namespaces['']), 3)
        self.assertIs(schema.elements['elem1'].schema, schema)
        self.assertIs(schema.elements['elem2'].schema, schema.maps.namespaces[''][1])
        self.assertIs(schema.elements['elem3'].schema, schema.maps.namespaces[''][2])

        # Insert the same schema twice has no effect anymore (skips the duplicate),
        # duplicates as detected by resource URL or identity (not for equality).
        schema = self.schema_class([source1, source2, source2])
        self.assertEqual(len(schema.elements), 2)
        self.assertEqual(len(schema.maps.namespaces['']), 2)
        self.assertIs(schema.elements['elem1'].schema, schema)
        self.assertIs(schema.elements['elem2'].schema, schema.maps.namespaces[''][1])

        source2a = '<?xml version="1.0" encoding="UTF-8"?>\n' + source2
        with self.assertRaises(XMLSchemaParseError) as ec:
            self.schema_class([source1, source2, source2a])
        self.assertIn("global xs:element with name='elem2' is already loaded",
                      str(ec.exception))

        source1 = dedent("""\
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
                    targetNamespace="http://xmlschema.test/ns">
                <xs:element name="elem1"/>
            </xs:schema>""")

        schema = self.schema_class([source1, source2])
        self.assertEqual(len(schema.elements), 1)
        self.assertEqual(len(schema.maps.namespaces['http://xmlschema.test/ns']), 1)
        self.assertIs(schema.elements['elem1'].schema, schema)
        self.assertIs(schema.maps.elements['elem2'].schema, schema.maps.namespaces[''][0])

    def test_add_schema(self):
        source1 = dedent("""\
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
                    targetNamespace="http://xmlschema.test/ns">
                <xs:element name="elem1"/>
            </xs:schema>""")

        source2 = dedent("""\
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
                <xs:element name="elem2"/>
            </xs:schema>""")

        source2_ = dedent("""\
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
                <xs:element name="elem2" />
            </xs:schema>""")

        source3 = dedent("""\
             <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
                     targetNamespace="http://xmlschema.test/ns1">
                 <xs:element name="elem3"/>
             </xs:schema>""")

        schema = self.schema_class(source1)

        # Provide a namespace, otherwise source2 is considered a chameleon schema
        schema.add_schema(source2, namespace='', build=True)
        self.assertEqual(len(schema.elements), 1)
        self.assertEqual(len(schema.maps.namespaces['http://xmlschema.test/ns']), 1)
        self.assertEqual(len(schema.maps.namespaces['']), 1)

        # Doesn't raise if the source is the same object
        schema.add_schema(source2, namespace='', build=True)
        self.assertEqual(len(schema.elements), 1)
        self.assertEqual(len(schema.maps.namespaces['http://xmlschema.test/ns']), 1)
        self.assertEqual(len(schema.maps.namespaces['']), 1)

        # Doesn't check equality of the sources, only URL matching.
        with self.assertRaises(XMLSchemaParseError) as ctx:
            schema.add_schema(source2_, namespace='', build=True)

        self.assertIn("global xs:element with name='elem2' is already loaded",
                      str(ctx.exception))

        with self.assertRaises(XMLSchemaParseError) as ec:
            schema.maps.clear()
            schema.build()
        self.assertIn("global xs:element with name='elem2' is already loaded",
                      str(ec.exception))

        schema = self.schema_class(source1)
        schema.add_schema(source2, namespace='http://xmlschema.test/ns', build=True)
        self.assertEqual(len(schema.maps.namespaces['http://xmlschema.test/ns']), 2)

        # Don't need a full rebuild to add elem2 from added schema ...
        self.assertEqual(len(schema.elements), 2)
        schema.maps.clear()
        schema.build()
        self.assertEqual(len(schema.elements), 2)

        # Or build after sources additions
        schema = self.schema_class(source1, build=False)
        schema.add_schema(source2, namespace='http://xmlschema.test/ns')
        schema.build()
        self.assertEqual(len(schema.elements), 2)

        # Adding other namespaces do not require rebuild
        schema3 = schema.add_schema(source3, build=True)
        self.assertEqual(len(schema.maps.namespaces['http://xmlschema.test/ns1']), 1)
        self.assertEqual(len(schema3.elements), 1)

    def test_pickling_invalid_schema(self):
        schema_file = self.cases_dir.joinpath('examples/vehicles/invalid.xsd')
        xml_file = self.cases_dir.joinpath('examples/vehicles/vehicles.xml')

        schema = self.schema_class(schema_file, validation='lax')
        self.assertTrue(schema.is_valid(str(xml_file)))

        s = pickle.dumps(schema)
        _schema = pickle.loads(s)
        self.assertTrue(_schema.is_valid(str(xml_file)))
        self.assertEqual(len(schema.errors), len(_schema.errors))

        err = XMLSchemaValidationError(schema, 'foo')
        schema.errors.append(err)  # noqa, not a parse error, only for checking unpickle correctness

        s = pickle.dumps(schema)
        _schema = pickle.loads(s)
        self.assertEqual(2, len(_schema.errors))

    def test_pickling_subclassed_schema__issue_263(self):
        schema_file = self.cases_dir.joinpath('examples/vehicles/vehicles.xsd')
        xml_file = self.cases_dir.joinpath('examples/vehicles/vehicles.xml')

        self.CustomXMLSchema.meta_schema.clear()
        schema = self.CustomXMLSchema(str(schema_file))
        self.assertTrue(schema.is_valid(str(xml_file)))

        self.assertIs(self.schema_class.meta_schema, schema.meta_schema)
        self.assertNotIn(schema.meta_schema.__class__.__name__, globals())

        s = pickle.dumps(schema)
        _schema = pickle.loads(s)
        self.assertTrue(_schema.is_valid(str(xml_file)))

        class CustomLocalXMLSchema(self.schema_class):
            pass

        schema = CustomLocalXMLSchema(str(schema_file))
        self.assertTrue(schema.is_valid(str(xml_file)))

        with self.assertRaises((pickle.PicklingError, AttributeError)) as ec:  # type: ignore
            pickle.dumps(schema)

        error_message = str(ec.exception)
        self.assertTrue(
            "Can't get local object" in error_message or "Can't pickle" in error_message
        )

    def test_meta_schema_validation(self):
        self.assertTrue(self.schema_class.meta_schema.is_valid(self.vh_xsd_file))

        invalid_xsd = self.casepath('examples/vehicles/invalid.xsd')
        self.assertFalse(self.schema_class.meta_schema.is_valid(invalid_xsd))

    def test_default_namespace_mapping__issue_266(self):
        schema_file = self.casepath('issues/issue_266/issue_266b-1.xsd')
        with self.assertRaises(XMLSchemaParseError) as ec:
            self.schema_class(schema_file)

        error_message = str(ec.exception)
        self.assertIn("the QName 'testAttribute3' is mapped to no namespace", error_message)
        self.assertIn("requires that there is an xs:import statement", error_message)

    @unittest.skipIf(SKIP_REMOTE_TESTS, "Remote networks are not accessible.")
    def test_import_dsig_namespace__issue_357(self):
        location = 'https://www.w3.org/TR/2008/REC-xmldsig-core-20080610/xmldsig-core-schema.xsd'
        dsig_namespace = 'http://www.w3.org/2000/09/xmldsig#'

        schema = self.schema_class(dedent(f"""<?xml version="1.0" encoding="UTF-8"?>
            <!-- Test import of defused data from remote with a fallback.-->
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
                <xs:import namespace="{dsig_namespace}"
                    schemaLocation="{location}"/>
                <xs:element name="root"/>
            </xs:schema>"""))

        self.assertIn(dsig_namespace, schema.maps.namespaces)
        url = schema.maps.namespaces[dsig_namespace][0].url
        self.assertIsInstance(url, str)
        self.assertTrue(url.endswith('schemas/DSIG/xmldsig-core-schema.xsd'))

    def test_include_overlap(self):
        schema = self.schema_class(dedent("""\
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
                <xs:element name="elem1"/>
                <xs:element name="elem2"/>
            </xs:schema>"""))

        with self.assertRaises(XMLSchemaParseError) as ctx:
            self.schema_class(dedent("""\
                <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
                    <xs:element name="elem1"/>
                    <xs:element name="elem2"/>
                </xs:schema>"""), global_maps=schema.maps)

        self.assertIn("global xs:element with name='elem1' is already loaded",
                      str(ctx.exception))

    def test_use_xpath3(self):
        schema = self.schema_class(dedent("""\
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
                <xs:element name="root"/>
            </xs:schema>"""), use_xpath3=True)

        self.assertTrue(schema.use_xpath3)

    def test_xmlns_namespace_forbidden(self):
        source = dedent("""\
             <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
                     targetNamespace="http://www.w3.org/2000/xmlns/">
                 <xs:element name="root"/>
             </xs:schema>""")

        with self.assertRaises(ValueError) as ctx:
            self.schema_class(source)

        self.assertIn('http://www.w3.org/2000/xmlns/', str(ctx.exception))

    def test_malformed_schema__issue_404(self):
        """Loads an xsd file"""
        malformed_xsd = self.casepath('resources/malformed.xsd')

        with self.assertRaises(xmlschema.XMLSchemaException):
            self.schema_class(malformed_xsd)

    def test_build_helpers_api(self):
        schema = self.schema_class(dedent("""\
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
                <xs:element name="root"/>
            </xs:schema>"""))
        xsd_element = schema.elements['root']

        self.assertIsInstance(
            schema.create_any_type(), XsdComplexType
        )
        self.assertIsInstance(
            schema.create_any_content_group(xsd_element.type), XsdGroup
        )
        self.assertIsInstance(
            schema.create_any_attribute_group(xsd_element), XsdAttributeGroup
        )
        self.assertIsInstance(
            schema.create_empty_attribute_group(xsd_element), XsdAttributeGroup
        )
        self.assertIsInstance(
            schema.create_empty_content_group(xsd_element.type), XsdGroup
        )
        self.assertIsInstance(
            schema.create_element('foo', xsd_element), XsdElement
        )

    def test_invalid_substitution_group__issue_452(self):

        with self.assertRaises(XMLSchemaParseError) as ctx:
            self.schema_class(dedent("""\
                <?xml version="1.0" encoding="utf-8"?>
                <schema xmlns="http://www.w3.org/2001/XMLSchema"
                        xmlns:w3="http://xmlschema.test/ns"
                        targetNamespace="http://xmlschema.test/ns"
                        elementFormDefault="qualified"
                        attributeFormDefault="unqualified">
                    <element id="x1" name="x1" nillable="true" type="integer" />
                    <element id="x2" name="x2" substitutionGroup="w3:x1" />
                    <element id="x3" name="x3" substitutionGroup="w3:x2" />
                    <element id="x4" name="x4" substitutionGroup="w3:x3" type="boolean"/>
                </schema>"""))
        self.assertIn("type is not of the same or a derivation of the head element",
                      str(ctx.exception))

        with self.assertRaises(XMLSchemaParseError) as ctx:
            self.schema_class(dedent("""\
                <?xml version="1.0" encoding="utf-8"?>
                <schema xmlns="http://www.w3.org/2001/XMLSchema"
                        xmlns:w3="http://xmlschema.test/ns"
                        targetNamespace="http://xmlschema.test/ns"
                        elementFormDefault="qualified"
                        attributeFormDefault="unqualified">
                    <element id="x1" name="x1" nillable="true" type="integer" />
                    <element id="x2" name="x2" substitutionGroup="w3:x1" />
                    <element id="x3" name="x4" substitutionGroup="w3:x2" type="boolean"/>
                </schema>"""))
        self.assertIn("type is not of the same or a derivation of the head element",
                      str(ctx.exception))

        with self.assertRaises(XMLSchemaParseError) as ctx:
            self.schema_class(dedent("""\
                <?xml version="1.0" encoding="utf-8"?>
                <schema xmlns="http://www.w3.org/2001/XMLSchema"
                        xmlns:w3="http://xmlschema.test/ns"
                        targetNamespace="http://xmlschema.test/ns"
                        elementFormDefault="qualified"
                        attributeFormDefault="unqualified">
                    <element id="x1" name="x1" nillable="true" type="integer" />
                    <element id="x2" name="x4" substitutionGroup="w3:x1" type="boolean"/>
                </schema>"""))
        self.assertIn("type is not of the same or a derivation of the head element",
                      str(ctx.exception))

        with self.assertRaises(XMLSchemaParseError) as ctx:
            self.schema_class(dedent("""\
                <?xml version="1.0" encoding="utf-8"?>
                <schema xmlns="http://www.w3.org/2001/XMLSchema"
                        xmlns:w3="http://xmlschema.test/ns"
                        targetNamespace="http://xmlschema.test/ns"
                        elementFormDefault="qualified"
                        attributeFormDefault="unqualified">
                    <element id="x1" name="x1" nillable="true" type="integer" />
                    <element id="x2" name="x4" substitutionGroup="w3:x1" type="anyType"/>
                </schema>"""))
        self.assertIn("type is not of the same or a derivation of the head element",
                      str(ctx.exception))

    def test_multiple_substitution_groups__issue_452(self):

        schema = self.schema_class(dedent("""\
            <?xml version="1.0" encoding="utf-8"?>
            <schema xmlns="http://www.w3.org/2001/XMLSchema"
                    xmlns:w3="http://xmlschema.test/ns"
                    targetNamespace="http://xmlschema.test/ns"
                    elementFormDefault="qualified"
                    attributeFormDefault="unqualified">
                <element id="x1" name="x1" nillable="true" type="decimal" />
                <element id="x2" name="x2" substitutionGroup="w3:x1" type="integer"/>
                <element id="x3" name="x3" substitutionGroup="w3:x2" type="int"/>
                <element id="x4" name="x4" substitutionGroup="w3:x3" type="short"/>
            </schema>"""))

        self.assertIsNone(schema.validate('<x4 xmlns="http://xmlschema.test/ns">8000</x4>'))

        with self.assertRaises(XMLSchemaValidationError) as ctx:
            schema.validate('<x4 xmlns="http://xmlschema.test/ns">80000</x4>')
        self.assertIn('failed validating 80000 with', str(ctx.exception))

        schema = self.schema_class(dedent("""\
            <?xml version="1.0" encoding="utf-8"?>
            <schema xmlns="http://www.w3.org/2001/XMLSchema"
                    xmlns:w3="http://xmlschema.test/ns"
                    targetNamespace="http://xmlschema.test/ns"
                    elementFormDefault="qualified"
                    attributeFormDefault="unqualified">
                <element id="x1" name="x1" nillable="true" type="decimal" />
                <element id="x2" name="x2" substitutionGroup="w3:x1"/>
            </schema>"""))

        # The effective type is not xs:anyType due to substitution: this may be an override
        # but the alternative requires more checks and an extra attribute for elements. This
        # happens only when the substitute element has no type explicitly associated.
        self.assertEqual(
            schema.elements['x2'].type.name, '{http://www.w3.org/2001/XMLSchema}decimal'
        )
        self.assertIsNone(schema.validate('<x2 xmlns="http://xmlschema.test/ns">80000</x2>'))

        with self.assertRaises(XMLSchemaValidationError) as ctx:
            schema.validate('<x2 xmlns="http://xmlschema.test/ns">foo</x2>')
        self.assertIn("invalid value 'foo'", str(ctx.exception))

    def test_substitution_groups_on_refs__issue_452(self):

        schema = self.schema_class(dedent("""\
            <?xml version="1.0" encoding="utf-8"?>
            <schema xmlns="http://www.w3.org/2001/XMLSchema"
                    xmlns:w3="http://xmlschema.test/ns"
                    targetNamespace="http://xmlschema.test/ns"
                    elementFormDefault="qualified"
                    attributeFormDefault="unqualified">
                <element id="x1" name="x1" nillable="true" type="integer" />
                <element id="x2" name="x2" substitutionGroup="w3:x1" type="short"/>

                <element name="values" type="w3:valuesType"/>
                <complexType name="valuesType">
                    <sequence>
                        <element ref="w3:x1" maxOccurs="unbounded"/>
                    </sequence>
                </complexType>
            </schema>"""))

        self.assertIsNone(schema.validate(
            '<values xmlns="http://xmlschema.test/ns"><x1>80000</x1></values>'
        ))
        self.assertIsNone(schema.validate(
            '<values xmlns="http://xmlschema.test/ns"><x2>8000</x2></values>'
        ))
        with self.assertRaises(XMLSchemaValidationError) as ctx:
            schema.validate(
                '<values xmlns="http://xmlschema.test/ns"><x2>80000</x2></values>'
            )
        self.assertIn('failed validating 80000 with', str(ctx.exception))


class TestXMLSchema11(TestXMLSchema10):

    schema_class = XMLSchema11

    class CustomXMLSchema(XMLSchema11):
        pass

    def test_default_attributes(self):
        schema = self.schema_class(dedent("""\
                    <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
                            defaultAttributes="attrs">
                        <xs:element name="root"/>
                        <xs:attributeGroup name="attrs">
                            <xs:attribute name="a"/>
                        </xs:attributeGroup>
                    </xs:schema>"""))
        self.assertIs(schema.default_attributes, schema.attribute_groups['attrs'])

        with self.assertRaises(XMLSchemaParseError) as ctx:
            self.schema_class(dedent("""\
                <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
                        defaultAttributes="attrs">
                    <xs:element name="root"/>
                </xs:schema>"""))
        self.assertIn("'attrs' doesn't match any attribute group", ctx.exception.message)

        with self.assertRaises(XMLSchemaParseError) as ctx:
            self.schema_class(dedent("""\
                <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
                        defaultAttributes="x:attrs">
                    <xs:element name="root"/>
                </xs:schema>"""))
        self.assertEqual("prefix 'x' not found in namespace map", ctx.exception.message)

    def test_use_xpath3(self):
        schema = self.schema_class(dedent("""\
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
                <xs:element name="root"/>
            </xs:schema>"""), use_xpath3=True)

        self.assertTrue(schema.use_xpath3)

        schema = self.schema_class(dedent("""\
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
                <xs:element name="root" type="rootType"/>
                <xs:complexType name="rootType">
                                  <xs:assert test="let $foo := 'bar' return $foo"/>

                </xs:complexType>
            </xs:schema>"""), use_xpath3=True)

        self.assertTrue(schema.use_xpath3)

        with self.assertRaises(XMLSchemaParseError) as ctx:
            self.schema_class(dedent("""\
                <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
                    <xs:element name="root" type="rootType"/>
                    <xs:complexType name="rootType">
                                      <xs:assert test="let $foo := 'bar' return $foo"/>

                    </xs:complexType>
                </xs:schema>"""))

        self.assertIn('XPST0003', str(ctx.exception))

    def test_xpath_predicate_selector__issue_454(self):
        schema_file = self.casepath('examples/vehicles/vehicles.xsd')
        xml_file = self.casepath('examples/vehicles/vehicles.xml')

        schema = self.schema_class(schema_file)
        with self.assertRaises(XMLSchemaValidationError) as ctx:
            schema.decode(xml_file, '/vh:vehicles/vh:bikes/vh:bike[2]')

        self.assertIn("maybe you have to provide a different path", ctx.exception.reason)


class TestXMLSchemaMeta(unittest.TestCase):

    def test_wrong_version(self):
        if sys.version_info < (3, 12):
            error_class = RuntimeError
            error_message = ("Error calling __set_name__ on 'XsdBuilders' "
                             "instance 'builders' in 'MetaXMLSchema12'")
        else:
            error_class = ValueError
            error_message = "wrong or unsupported XSD version '1.2'"

        with self.assertRaises(error_class) as ctx:
            class XMLSchema12(XMLSchemaBase):
                XSD_VERSION = '1.2'
                builders = XsdBuilders()
                meta_schema = os.path.join(SCHEMAS_DIR, 'XSD_1.1/XMLSchema.xsd')

            assert issubclass(XMLSchema12, XMLSchemaBase)

        self.assertEqual(str(ctx.exception), error_message)

    def test_from_schema_class(self):
        class XMLSchema11Bis(XMLSchema11):
            pass

        self.assertTrue(issubclass(XMLSchema11Bis, XMLSchemaBase))

    def test_dummy_validator_class(self):

        class DummySchema(XMLSchemaBase):
            builders = XsdBuilders()
            XSD_VERSION = '1.1'
            meta_schema = os.path.join(SCHEMAS_DIR, 'XSD_1.1/XMLSchema.xsd')

        self.assertTrue(issubclass(DummySchema, XMLSchemaBase))

    def test_subclass_but_no_replace_meta_schema(self):

        class CustomXMLSchema10(XMLSchema10):
            builders = XsdBuilders()

        self.assertIsInstance(CustomXMLSchema10.meta_schema, XMLSchemaBase)
        self.assertIs(CustomXMLSchema10.meta_schema, XMLSchema10.meta_schema)

        name = CustomXMLSchema10.meta_schema.__class__.__name__
        self.assertEqual(name, 'MetaXMLSchema10')
        self.assertNotIn(name, globals())

    def test_subclass_and_replace_meta_schema(self):

        class CustomXMLSchema10(XMLSchema10):
            builders = XsdBuilders()
            META_SCHEMA = os.path.join(SCHEMAS_DIR, 'XSD_1.0/XMLSchema.xsd')

        self.assertIsInstance(CustomXMLSchema10.meta_schema, XMLSchemaBase)
        self.assertIsNot(CustomXMLSchema10.meta_schema, XMLSchema10.meta_schema)

        name = CustomXMLSchema10.meta_schema.__class__.__name__
        self.assertEqual(name, 'MetaCustomXMLSchema10')
        self.assertIn(name, globals())

        bases = CustomXMLSchema10.meta_schema.__class__.__bases__
        self.assertEqual(bases, (XMLSchema10.meta_schema.__class__,))

    def test_subclass_and_create_base_meta_schema(self):

        class CustomXMLSchema10(XMLSchemaBase):
            builders = XsdBuilders()
            META_SCHEMA = os.path.join(SCHEMAS_DIR, 'XSD_1.0/XMLSchema.xsd')

        self.assertIsInstance(CustomXMLSchema10.meta_schema, XMLSchemaBase)
        self.assertIsNot(CustomXMLSchema10.meta_schema, XMLSchema10.meta_schema)

        name = CustomXMLSchema10.meta_schema.__class__.__name__
        self.assertEqual(name, 'MetaCustomXMLSchema10')
        self.assertIn(name, globals())

        bases = CustomXMLSchema10.meta_schema.__class__.__bases__
        self.assertEqual(bases, (XMLSchemaBase,))


if __name__ == '__main__':
    from xmlschema.testing import run_xmlschema_tests
    run_xmlschema_tests('schema classes')
