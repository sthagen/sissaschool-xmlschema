#!/usr/bin/env python
#
# Copyright (c), 2018-2020, SISSA (International School for Advanced Studies).
# All rights reserved.
# This file is distributed under the terms of the MIT License.
# See the file 'LICENSE' in the root directory of the present
# distribution, or http://opensource.org/licenses/MIT.
#
# @author Davide Brunato <brunato@sissa.it>
#
import unittest
import xml.etree.ElementTree as ElementTree
from pathlib import Path

try:
    import lxml.etree as lxml_etree
except ImportError:
    lxml_etree = None

from xmlschema import XMLSchema, XMLSchemaValidationError, fetch_namespaces
from xmlschema.etree import etree_element
from xmlschema.dataobjects import DataElement
from xmlschema.testing import etree_elements_assert_equal

from xmlschema.converters import XMLSchemaConverter, UnorderedConverter, \
    ParkerConverter, BadgerFishConverter, AbderaConverter, JsonMLConverter, \
    ColumnarConverter
from xmlschema.dataobjects import DataElementConverter


class TestConverters(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.col_xsd_filename = cls.casepath('examples/collection/collection.xsd')
        cls.col_xml_filename = cls.casepath('examples/collection/collection.xml')
        cls.col_xml_root = ElementTree.parse(cls.col_xml_filename).getroot()
        cls.col_lxml_root = lxml_etree.parse(cls.col_xml_filename).getroot()
        cls.col_nsmap = fetch_namespaces(cls.col_xml_filename)
        cls.col_namespace = cls.col_nsmap['col']

    @classmethod
    def casepath(cls, relative_path):
        return str(Path(__file__).parent.joinpath('test_cases', relative_path))

    def test_element_class_argument(self):
        converter = XMLSchemaConverter()
        self.assertIs(converter.etree_element_class, etree_element)

        converter = XMLSchemaConverter(etree_element_class=etree_element)
        self.assertIs(converter.etree_element_class, etree_element)

        if lxml_etree is not None:
            converter = XMLSchemaConverter(etree_element_class=lxml_etree.Element)
            self.assertIs(converter.etree_element_class, lxml_etree.Element)

    def test_prefix_arguments(self):
        converter = XMLSchemaConverter(cdata_prefix='#')
        self.assertEqual(converter.cdata_prefix, '#')

        converter = XMLSchemaConverter(attr_prefix='%')
        self.assertEqual(converter.attr_prefix, '%')

        converter = XMLSchemaConverter(attr_prefix='_')
        self.assertEqual(converter.attr_prefix, '_')

        converter = XMLSchemaConverter(attr_prefix='attribute__')
        self.assertEqual(converter.attr_prefix, 'attribute__')

        converter = XMLSchemaConverter(text_key='text__')
        self.assertEqual(converter.text_key, 'text__')

    def test_strip_namespace_argument(self):
        # Test for issue #161
        converter = XMLSchemaConverter(strip_namespaces=True)
        col_xsd_filename = self.casepath('examples/collection/collection.xsd')
        col_xml_filename = self.casepath('examples/collection/collection.xml')

        col_schema = XMLSchema(col_xsd_filename, converter=converter)
        self.assertIn('@xmlns:', str(col_schema.decode(col_xml_filename, strip_namespaces=False)))
        self.assertNotIn('@xmlns:', str(col_schema.decode(col_xml_filename)))

    def test_lossy_property(self):
        self.assertTrue(XMLSchemaConverter().lossy)
        self.assertFalse(XMLSchemaConverter(cdata_prefix='#').lossy)

    def test_cdata_mapping(self):
        schema = XMLSchema("""
        <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
            <xs:element name="root">
                <xs:complexType mixed="true">
                    <xs:sequence>
                        <xs:element name="node" type="xs:string" maxOccurs="unbounded"/>
                    </xs:sequence>
                </xs:complexType>
            </xs:element>
        </xs:schema> 
        """)

        self.assertEqual(
            schema.decode('<root>1<node/>2<node/>3</root>'), {'node': [None, None]}
        )
        self.assertEqual(
            schema.decode('<root>1<node/>2<node/>3</root>', cdata_prefix='#'),
            {'#1': '1', 'node': [None, None], '#2': '2', '#3': '3'}
        )

    def test_preserve_root__issue_215(self):
        schema = XMLSchema("""
        <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" 
                   xmlns="http://xmlschema.test/ns"
                   targetNamespace="http://xmlschema.test/ns">
            <xs:element name="a">
                <xs:complexType>
                    <xs:sequence>
                        <xs:element name="b1" type="xs:string" maxOccurs="unbounded"/>
                        <xs:element name="b2" type="xs:string" maxOccurs="unbounded"/>
                    </xs:sequence>
                </xs:complexType>
            </xs:element>
        </xs:schema> 
        """)

        xml_data = """<tns:a xmlns:tns="http://xmlschema.test/ns"><b1/><b2/></tns:a>"""

        obj = schema.decode(xml_data)
        self.assertListEqual(list(obj), ['@xmlns:tns', 'b1', 'b2'])
        self.assertEqual(schema.encode(obj).tag, '{http://xmlschema.test/ns}a')

        obj = schema.decode(xml_data, preserve_root=True)
        self.assertListEqual(list(obj), ['tns:a'])

        root = schema.encode(obj, preserve_root=True, path='tns:a',
                             namespaces={'tns': 'http://xmlschema.test/ns'})
        self.assertEqual(root.tag, '{http://xmlschema.test/ns}a')

        root = schema.encode(obj, preserve_root=True, path='{http://xmlschema.test/ns}a')
        self.assertEqual(root.tag, '{http://xmlschema.test/ns}a')

        root = schema.encode(obj, preserve_root=True)
        self.assertEqual(root.tag, '{http://xmlschema.test/ns}a')

    def test_etree_element_method(self):
        converter = XMLSchemaConverter()
        elem = converter.etree_element('A')
        self.assertIsNone(etree_elements_assert_equal(elem, etree_element('A')))

        elem = converter.etree_element('A', attrib={})
        self.assertIsNone(etree_elements_assert_equal(elem, etree_element('A')))

    def test_columnar_converter(self):
        col_schema = XMLSchema(self.col_xsd_filename, converter=ColumnarConverter)

        obj = col_schema.decode(self.col_xml_filename)
        self.assertIn("'authorid'", str(obj))
        self.assertNotIn("'author_id'", str(obj))
        self.assertNotIn("'author__id'", str(obj))

        obj = col_schema.decode(self.col_xml_filename, attr_prefix='_')
        self.assertNotIn("'authorid'", str(obj))
        self.assertIn("'author_id'", str(obj))
        self.assertNotIn("'author__id'", str(obj))

        obj = col_schema.decode(self.col_xml_filename, attr_prefix='__')
        self.assertNotIn("'authorid'", str(obj))
        self.assertNotIn("'author_id'", str(obj))
        self.assertIn("'author__id'", str(obj))

        col_schema = XMLSchema(self.col_xsd_filename)

        obj = col_schema.decode(self.col_xml_filename, converter=ColumnarConverter,
                                attr_prefix='__')
        self.assertNotIn("'authorid'", str(obj))
        self.assertNotIn("'author_id'", str(obj))
        self.assertIn("'author__id'", str(obj))

    def test_data_element_converter(self):
        col_schema = XMLSchema(self.col_xsd_filename, converter=DataElementConverter)
        obj = col_schema.decode(self.col_xml_filename)

        self.assertIsInstance(obj, DataElement)
        self.assertEqual(obj.tag, self.col_xml_root.tag)
        self.assertEqual(obj.nsmap, self.col_nsmap)

    def test_decode_encode_default_converter(self):
        col_schema = XMLSchema(self.col_xsd_filename)

        # Decode from XML file
        obj1 = col_schema.decode(self.col_xml_filename)
        self.assertIn("'@xmlns:col'", repr(obj1))

        root = col_schema.encode(obj1, path='./col:collection', namespaces=self.col_nsmap)
        self.assertIsNone(etree_elements_assert_equal(self.col_xml_root, root, strict=False))

        root = col_schema.encode(obj1)
        self.assertIsNone(etree_elements_assert_equal(self.col_xml_root, root, strict=False))

        # Decode from lxml.etree.Element tree
        obj2 = col_schema.decode(self.col_lxml_root)
        self.assertIn("'@xmlns:col'", repr(obj2))
        self.assertEqual(obj1, obj2)

        # Decode from ElementTree.Element tree providing namespaces
        obj2 = col_schema.decode(self.col_xml_root, namespaces=self.col_nsmap)
        self.assertIn("'@xmlns:col'", repr(obj2))
        self.assertEqual(obj1, obj2)

        # Decode from ElementTree.Element tree without namespaces
        obj2 = col_schema.decode(self.col_xml_root)
        self.assertNotIn("'@xmlns:col'", repr(obj2))
        self.assertNotEqual(obj1, obj2)

        root = col_schema.encode(obj2, path='./col:collection', namespaces=self.col_nsmap)
        self.assertIsNone(etree_elements_assert_equal(self.col_xml_root, root, strict=False))

        root = col_schema.encode(obj2)  # No namespace unmap is required
        self.assertIsNone(etree_elements_assert_equal(self.col_xml_root, root, strict=False))

    def test_decode_encode_default_converter_with_preserve_root(self):
        col_schema = XMLSchema(self.col_xsd_filename)

        # Decode from XML file
        obj1 = col_schema.decode(self.col_xml_filename, preserve_root=True)
        self.assertIn("'col:collection'", repr(obj1))
        self.assertIn("'@xmlns:col'", repr(obj1))

        root = col_schema.encode(obj1, path='./col:collection', namespaces=self.col_nsmap,
                                 preserve_root=True)
        self.assertIsNone(etree_elements_assert_equal(self.col_xml_root, root, strict=False))

        root = col_schema.encode(obj1, preserve_root=True)
        self.assertIsNone(etree_elements_assert_equal(self.col_xml_root, root, strict=False))

        # Decode from lxml.etree.Element tree
        obj2 = col_schema.decode(self.col_lxml_root, preserve_root=True)
        self.assertIn("'col:collection'", repr(obj2))
        self.assertIn("'@xmlns:col'", repr(obj2))
        self.assertEqual(obj1, obj2)

        # Decode from ElementTree.Element tree providing namespaces
        obj2 = col_schema.decode(self.col_xml_root, namespaces=self.col_nsmap, preserve_root=True)
        self.assertIn("'col:collection'", repr(obj2))
        self.assertIn("'@xmlns:col'", repr(obj2))
        self.assertEqual(obj1, obj2)

        # Decode from ElementTree.Element tree without namespaces
        obj2 = col_schema.decode(self.col_xml_root, preserve_root=True)
        self.assertNotIn("'col:collection'", repr(obj2))
        self.assertNotIn("'@xmlns:col'", repr(obj2))
        self.assertNotEqual(obj1, obj2)

        root = col_schema.encode(obj2, path='./col:collection',
                                 namespaces=self.col_nsmap, preserve_root=True)
        self.assertIsNone(etree_elements_assert_equal(self.col_xml_root, root, strict=False))

        root = col_schema.encode(obj2, preserve_root=True)  # No namespace unmap is required
        self.assertIsNone(etree_elements_assert_equal(self.col_xml_root, root, strict=False))

    def test_decode_encode_unordered_converter(self):
        col_schema = XMLSchema(self.col_xsd_filename, converter=UnorderedConverter)

        # Decode from XML file
        obj1 = col_schema.decode(self.col_xml_filename)
        self.assertIn("'@xmlns:col'", repr(obj1))

        root = col_schema.encode(obj1, path='./col:collection', namespaces=self.col_nsmap)
        self.assertIsNone(etree_elements_assert_equal(self.col_xml_root, root, strict=False))

        root = col_schema.encode(obj1)
        self.assertIsNone(etree_elements_assert_equal(self.col_xml_root, root, strict=False))

        # Decode from lxml.etree.Element tree
        obj2 = col_schema.decode(self.col_lxml_root)
        self.assertIn("'@xmlns:col'", repr(obj2))
        self.assertEqual(obj1, obj2)

        # Decode from ElementTree.Element tree providing namespaces
        obj2 = col_schema.decode(self.col_xml_root, namespaces=self.col_nsmap)
        self.assertIn("'@xmlns:col'", repr(obj2))
        self.assertEqual(obj1, obj2)

        # Decode from ElementTree.Element tree without namespaces
        obj2 = col_schema.decode(self.col_xml_root)
        self.assertNotIn("'@xmlns:col'", repr(obj2))
        self.assertNotEqual(obj1, obj2)

        root = col_schema.encode(obj2, path='./col:collection', namespaces=self.col_nsmap)
        self.assertIsNone(etree_elements_assert_equal(self.col_xml_root, root, strict=False))

        root = col_schema.encode(obj2)  # No namespace unmap is required
        self.assertIsNone(etree_elements_assert_equal(self.col_xml_root, root, strict=False))

    def test_decode_encode_unordered_converter_with_preserve_root(self):
        col_schema = XMLSchema(self.col_xsd_filename, converter=UnorderedConverter)

        # Decode from XML file
        obj1 = col_schema.decode(self.col_xml_filename, preserve_root=True)
        self.assertIn("'col:collection'", repr(obj1))
        self.assertIn("'@xmlns:col'", repr(obj1))

        root = col_schema.encode(obj1, path='./col:collection', namespaces=self.col_nsmap,
                                 preserve_root=True)
        self.assertIsNone(etree_elements_assert_equal(self.col_xml_root, root, strict=False))

        root = col_schema.encode(obj1, preserve_root=True)
        self.assertIsNone(etree_elements_assert_equal(self.col_xml_root, root, strict=False))

        # Decode from lxml.etree.Element tree
        obj2 = col_schema.decode(self.col_lxml_root, preserve_root=True)
        self.assertIn("'col:collection'", repr(obj2))
        self.assertIn("'@xmlns:col'", repr(obj2))
        self.assertEqual(obj1, obj2)

        # Decode from ElementTree.Element tree providing namespaces
        obj2 = col_schema.decode(self.col_xml_root, namespaces=self.col_nsmap, preserve_root=True)
        self.assertIn("'col:collection'", repr(obj2))
        self.assertIn("'@xmlns:col'", repr(obj2))
        self.assertEqual(obj1, obj2)

        # Decode from ElementTree.Element tree without namespaces
        obj2 = col_schema.decode(self.col_xml_root, preserve_root=True)
        self.assertNotIn("'col:collection'", repr(obj2))
        self.assertNotIn("'@xmlns:col'", repr(obj2))
        self.assertNotEqual(obj1, obj2)

        root = col_schema.encode(obj2, path='./col:collection',
                                 namespaces=self.col_nsmap, preserve_root=True)
        self.assertIsNone(etree_elements_assert_equal(self.col_xml_root, root, strict=False))

        root = col_schema.encode(obj2, preserve_root=True)  # No namespace unmap is required
        self.assertIsNone(etree_elements_assert_equal(self.col_xml_root, root, strict=False))

    def test_decode_encode_parker_converter(self):
        col_schema = XMLSchema(self.col_xsd_filename, converter=ParkerConverter)

        obj1 = col_schema.decode(self.col_xml_filename)

        with self.assertRaises(XMLSchemaValidationError) as ec:
            col_schema.encode(obj1, path='./col:collection', namespaces=self.col_nsmap)
        self.assertIn("missing required attribute 'id'", str(ec.exception))

    def test_decode_encode_badger_fish_converter(self):
        col_schema = XMLSchema(self.col_xsd_filename, converter=BadgerFishConverter)

        obj1 = col_schema.decode(self.col_xml_filename)
        self.assertIn("'@xmlns'", repr(obj1))

        root = col_schema.encode(obj1, path='./col:collection', namespaces=self.col_nsmap)
        self.assertIsNone(etree_elements_assert_equal(self.col_xml_root, root, strict=False))

        root = col_schema.encode(obj1)
        self.assertIsNone(etree_elements_assert_equal(self.col_xml_root, root, strict=False))

        # With ElementTree namespaces are not mapped
        obj2 = col_schema.decode(self.col_xml_root)
        self.assertNotIn("'@xmlns'", repr(obj2))
        self.assertNotEqual(obj1, obj2)
        self.assertEqual(obj1, col_schema.decode(self.col_xml_root, namespaces=self.col_nsmap))

        # With lxml.etree namespaces are mapped
        self.assertEqual(obj1, col_schema.decode(self.col_lxml_root))

        root = col_schema.encode(obj2, path='./col:collection', namespaces=self.col_nsmap)
        self.assertIsNone(etree_elements_assert_equal(self.col_xml_root, root, strict=False))

        root = col_schema.encode(obj2)  # No namespace unmap is required
        self.assertIsNone(etree_elements_assert_equal(self.col_xml_root, root, strict=False))

    def test_decode_encode_abdera_converter(self):
        col_schema = XMLSchema(self.col_xsd_filename, converter=AbderaConverter)

        obj1 = col_schema.decode(self.col_xml_filename)

        root = col_schema.encode(obj1, path='./col:collection', namespaces=self.col_nsmap)
        self.assertIsNone(etree_elements_assert_equal(self.col_xml_root, root, strict=False))

        # Namespace mapping is required
        with self.assertRaises(XMLSchemaValidationError) as ec:
            col_schema.encode(obj1, path='./{%s}collection' % self.col_namespace)
        self.assertIn("'xsi:schemaLocation' attribute not allowed", str(ec.exception))

        # With ElementTree namespaces are not mapped
        obj2 = col_schema.decode(self.col_xml_root)
        self.assertNotEqual(obj1, obj2)
        self.assertEqual(obj1, col_schema.decode(self.col_xml_root, namespaces=self.col_nsmap))

        # With lxml.etree namespaces are mapped
        self.assertEqual(obj1, col_schema.decode(self.col_lxml_root))

        root = col_schema.encode(obj2, path='./col:collection', namespaces=self.col_nsmap)
        self.assertIsNone(etree_elements_assert_equal(self.col_xml_root, root, strict=False))

        root = col_schema.encode(obj2)  # No namespace unmap is required
        self.assertIsNone(etree_elements_assert_equal(self.col_xml_root, root, strict=False))

    def test_decode_encode_jsonml_converter(self):
        col_schema = XMLSchema(self.col_xsd_filename, converter=JsonMLConverter)

        obj1 = col_schema.decode(self.col_xml_filename)
        self.assertIn('col:collection', repr(obj1))
        self.assertIn('xmlns:col', repr(obj1))

        root = col_schema.encode(obj1, path='./col:collection', namespaces=self.col_nsmap)
        self.assertIsNone(etree_elements_assert_equal(self.col_xml_root, root, strict=False))

        root = col_schema.encode(obj1, path='./{%s}collection' % self.col_namespace)
        self.assertIsNone(etree_elements_assert_equal(self.col_xml_root, root, strict=False))

        root = col_schema.encode(obj1)
        self.assertIsNone(etree_elements_assert_equal(self.col_xml_root, root, strict=False))

        # With ElementTree namespaces are not mapped
        obj2 = col_schema.decode(self.col_xml_root)
        self.assertNotIn('col:collection', repr(obj2))
        self.assertNotEqual(obj1, obj2)
        self.assertEqual(obj1, col_schema.decode(self.col_xml_root, namespaces=self.col_nsmap))

        # With lxml.etree namespaces are mapped
        self.assertEqual(obj1, col_schema.decode(self.col_lxml_root))

        root = col_schema.encode(obj2, path='./col:collection', namespaces=self.col_nsmap)
        self.assertIsNone(etree_elements_assert_equal(self.col_xml_root, root, strict=False))

        root = col_schema.encode(obj2)  # No namespace unmap is required
        self.assertIsNone(etree_elements_assert_equal(self.col_xml_root, root, strict=False))

    def test_decode_encode_columnar_converter(self):
        col_schema = XMLSchema(self.col_xsd_filename, converter=ColumnarConverter)

        obj1 = col_schema.decode(self.col_xml_filename)

        root = col_schema.encode(obj1, path='./col:collection', namespaces=self.col_nsmap)
        self.assertIsNone(etree_elements_assert_equal(self.col_xml_root, root, strict=False))

        # Namespace mapping is required
        with self.assertRaises(XMLSchemaValidationError) as ec:
            col_schema.encode(obj1, path='./{%s}collection' % self.col_namespace)
        self.assertIn("'xsi:schemaLocation' attribute not allowed", str(ec.exception))

        # With ElementTree namespaces are not mapped
        obj2 = col_schema.decode(self.col_xml_root)
        self.assertNotEqual(obj1, obj2)
        self.assertEqual(obj1, col_schema.decode(self.col_xml_root, namespaces=self.col_nsmap))

        # With lxml.etree namespaces are mapped
        self.assertEqual(obj1, col_schema.decode(self.col_lxml_root))

        root = col_schema.encode(obj2, path='./col:collection', namespaces=self.col_nsmap)
        self.assertIsNone(etree_elements_assert_equal(self.col_xml_root, root, strict=False))

        root = col_schema.encode(obj2)  # No namespace unmap is required
        self.assertIsNone(etree_elements_assert_equal(self.col_xml_root, root, strict=False))

    def test_decode_encode_data_element_converter(self):
        col_schema = XMLSchema(self.col_xsd_filename, converter=DataElementConverter)

        obj1 = col_schema.decode(self.col_xml_filename)
        # self.assertIn('col:collection', repr(obj1))
        self.assertIn('col', obj1.nsmap)

        root = col_schema.encode(obj1, path='./col:collection', namespaces=self.col_nsmap)

        self.assertIsNone(etree_elements_assert_equal(self.col_xml_root, root, strict=False))

        root = col_schema.encode(obj1, path='./{%s}collection' % self.col_namespace)
        self.assertIsNone(etree_elements_assert_equal(self.col_xml_root, root, strict=False))

        root = col_schema.encode(obj1)
        self.assertIsNone(etree_elements_assert_equal(self.col_xml_root, root, strict=False))

        # With ElementTree namespaces are not mapped
        obj2 = col_schema.decode(self.col_xml_root)

        # Equivalent if compared as Element trees (tag, text, attrib, tail)
        self.assertIsNone(etree_elements_assert_equal(obj1, obj2))

        self.assertIsNone(etree_elements_assert_equal(
            obj1, col_schema.decode(self.col_xml_root, namespaces=self.col_nsmap)
        ))

        # With lxml.etree namespaces are mapped
        self.assertIsNone(etree_elements_assert_equal(
            obj1, col_schema.decode(self.col_lxml_root)
        ))

        root = col_schema.encode(obj2, path='./col:collection', namespaces=self.col_nsmap)
        self.assertIsNone(etree_elements_assert_equal(self.col_xml_root, root, strict=False))

        root = col_schema.encode(obj2)  # No namespace unmap is required
        self.assertIsNone(etree_elements_assert_equal(self.col_xml_root, root, strict=False))


if __name__ == '__main__':
    import platform
    header_template = "Test xmlschema converters with Python {} on {}"
    header = header_template.format(platform.python_version(), platform.platform())
    print('{0}\n{1}\n{0}'.format("*" * len(header), header))

    unittest.main()
