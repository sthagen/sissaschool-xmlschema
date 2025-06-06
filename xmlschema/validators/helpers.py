#
# Copyright (c), 2016-2020, SISSA (International School for Advanced Studies).
# All rights reserved.
# This file is distributed under the terms of the MIT License.
# See the file 'LICENSE' in the root directory of the present
# distribution, or http://opensource.org/licenses/MIT.
#
# @author Davide Brunato <brunato@sissa.it>
#
from decimal import Decimal
from math import isinf, isnan
from typing import Optional, SupportsInt, SupportsFloat, Union
from xml.etree.ElementTree import Element
from elementpath import datatypes

from xmlschema.aliases import ElementType
from xmlschema.names import XSD_ANNOTATION
from xmlschema.exceptions import XMLSchemaValueError
from xmlschema.translation import gettext as _
from .exceptions import XMLSchemaValidationError

XSD_FINAL_ATTRIBUTE_VALUES = {'restriction', 'extension', 'list', 'union'}
XSD_BOOLEAN_MAP = {
    'false': False, '0': False,
    'true': True, '1': True
}


def get_xsd_derivation_attribute(elem: Element, attribute: str,
                                 values: Optional[set[str]] = None) -> str:
    """
    Get a derivation attribute (maybe 'block', 'blockDefault', 'final' or 'finalDefault')
    checking the items with the values arguments. Returns a string.

    :param elem: the Element instance.
    :param attribute: the attribute name.
    :param values: a set of admitted values when the attribute value is not '#all'.
    """
    value = elem.get(attribute)
    if value is None:
        return ''

    if values is None:
        values = XSD_FINAL_ATTRIBUTE_VALUES

    items = value.split()
    if len(items) == 1 and items[0] == '#all':
        return ' '.join(values)
    elif not all(s in values for s in items):
        raise ValueError(_("wrong value %r for attribute %r") % (value, attribute))
    return value


def get_xsd_annotation_child(elem: ElementType) -> Optional[ElementType]:
    """
    Returns the child element of the annotation associated to an XSD component,
    `None` if it doesn't exist.
    """
    for child in elem:
        if child.tag == XSD_ANNOTATION:
            return child
        elif not callable(child.tag):
            return None
    else:
        return None


#
# XSD built-in types validator functions

def decimal_validator(value: Union[Decimal, int, float, str]) -> None:
    try:
        if not isinstance(value, (Decimal, float)):
            datatypes.DecimalProxy.validate(value)
        elif isinf(value) or isnan(value):
            raise ValueError()
    except (ValueError, TypeError):
        raise XMLSchemaValidationError(decimal_validator, value,
                                       _("value is not a valid xs:decimal")) from None


def qname_validator(value: str) -> None:
    if datatypes.QName.pattern.match(value) is None:
        raise XMLSchemaValidationError(qname_validator, value,
                                       _("value is not an xs:QName"))


def byte_validator(value: int) -> None:
    if not (-2**7 <= value < 2 ** 7):
        raise XMLSchemaValidationError(int_validator, value,
                                       _("value must be {:s}").format("-128 <= x < 128"))


def short_validator(value: int) -> None:
    if not (-2**15 <= value < 2 ** 15):
        raise XMLSchemaValidationError(short_validator, value,
                                       _("value must be {:s}").format("-2^15 <= x < 2^15"))


def int_validator(value: int) -> None:
    if not (-2**31 <= value < 2 ** 31):
        raise XMLSchemaValidationError(int_validator, value,
                                       _("value must be {:s}").format("-2^31 <= x < 2^31"))


def long_validator(value: int) -> None:
    if not (-2**63 <= value < 2 ** 63):
        raise XMLSchemaValidationError(long_validator, value,
                                       _("value must be {:s}").format("-2^63 <= x < 2^63"))


def unsigned_byte_validator(value: int) -> None:
    if not (0 <= value < 2 ** 8):
        raise XMLSchemaValidationError(unsigned_byte_validator, value,
                                       _("value must be {:s}").format("0 <= x < 256"))


def unsigned_short_validator(value: int) -> None:
    if not (0 <= value < 2 ** 16):
        raise XMLSchemaValidationError(unsigned_short_validator, value,
                                       _("value must be {:s}").format("0 <= x < 2^16"))


def unsigned_int_validator(value: int) -> None:
    if not (0 <= value < 2 ** 32):
        raise XMLSchemaValidationError(unsigned_int_validator, value,
                                       _("value must be {:s}").format("0 <= x < 2^32"))


def unsigned_long_validator(value: int) -> None:
    if not (0 <= value < 2 ** 64):
        raise XMLSchemaValidationError(unsigned_long_validator, value,
                                       _("value must be {:s}").format("0 <= x < 2^64"))


def negative_int_validator(value: int) -> None:
    if value >= 0:
        raise XMLSchemaValidationError(negative_int_validator, value,
                                       _("value must be negative"))


def positive_int_validator(value: int) -> None:
    if value <= 0:
        raise XMLSchemaValidationError(positive_int_validator, value,
                                       _("value must be positive"))


def non_positive_int_validator(value: int) -> None:
    if value > 0:
        raise XMLSchemaValidationError(non_positive_int_validator, value,
                                       _("value must be non positive"))


def non_negative_int_validator(value: int) -> None:
    if value < 0:
        raise XMLSchemaValidationError(non_negative_int_validator, value,
                                       _("value must be non negative"))


def hex_binary_validator(value: Union[str, datatypes.HexBinary]) -> None:
    if not isinstance(value, datatypes.HexBinary) and \
            datatypes.HexBinary.pattern.match(value) is None:
        raise XMLSchemaValidationError(hex_binary_validator, value,
                                       _("not an hexadecimal number"))


def base64_binary_validator(value: Union[str, datatypes.Base64Binary]) -> None:
    if isinstance(value, datatypes.Base64Binary):
        return
    value = value.replace(' ', '')
    if not value:
        return

    match = datatypes.Base64Binary.pattern.match(value)
    if match is None or match.group(0) != value:
        raise XMLSchemaValidationError(base64_binary_validator, value,
                                       _("not a base64 encoding"))


def error_type_validator(value: object) -> None:
    raise XMLSchemaValidationError(error_type_validator, value,
                                   _("no value is allowed for xs:error type"))


#
# XSD builtin decoding functions

def boolean_to_python(value: str) -> bool:
    try:
        return XSD_BOOLEAN_MAP[value]
    except KeyError:
        raise XMLSchemaValueError(_('{!r} is not a boolean value').format(value))


def python_to_boolean(value: object) -> str:
    if isinstance(value, str):
        if value in XSD_BOOLEAN_MAP:
            return value
        raise XMLSchemaValueError(_('{!r} is not a boolean value').format(value))
    return str(value).lower()


def python_to_float(value: Union[SupportsFloat, str]) -> str:
    if isinstance(value, str):
        if value in ('NaN', 'INF', '-INF'):
            return value
        return str(float(value))
    elif isnan(value):
        return "NaN"
    if value == float("inf"):
        return "INF"
    if value == float("-inf"):
        return "-INF"
    return str(value)


def python_to_int(value: Union[SupportsInt, str]) -> str:
    return str(int(value))
