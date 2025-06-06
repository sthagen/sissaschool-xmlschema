#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# xmlschema documentation build configuration file, created by
# sphinx-quickstart on Fri Jan 12 09:05:46 2018.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

# Extends the path with parent directory in order to
# import xmlschema from the project also if it's installed.
import sys
import os
sys.path.insert(0, os.path.abspath('..'))

# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.doctest']

# Option for autodoc: do not add module name as prefix to classes or functions.
add_module_names = False

nitpick_ignore = [
    ('py:class', 'collections.abc.Callable'),
    ('py:class', 'pathlib.Path'),
    ('py:class', 'collections.Counter'),
    ('py:class', 'decimal.Decimal'),
    ('py:class', 'xml.etree.ElementTree.Element'),
    ('py:class', 'xml.etree.ElementTree.ElementTree'),
    ('py:class', 'xmlschema.aliases.T'),
    ('py:class', 'xmlschema.xpath.mixin.E_co'),
    ('py:class', 'xmlschema.validators.xsdbase.DT'),
    ('py:class', 'xmlschema.validators.xsdbase.ST'),
    ('py:class', 'XsdValidator'),
    ('py:class', 'XMLSchemaMeta'),
    ('py:class', 'BaseXsdType'),
    ('py:class', 'ElementType'),
    ('py:class', 'xmlschema.validators.schemas.XMLSchema10'),
    ('py:class', 'xmlschema.loaders.SchemaLoader'),
    ('py:class', 'urllib.request.OpenerDirector'),
    ('py:class', 'xmlschema.utils.protocols.IOProtocol'),
    ('py:class', 'xmlschema.validators.builders.XsdBuilders'),
    ('py:class', 'SchemaLoader'),
    ('py:class', 'OpenerDirector'),
    ('py:class', 'xmlschema.validators.builders.SchemaConfig'),
    ('py:meth', 'read'),
    ('py:meth', 'write'),
    ('py:obj', 'typing.IO'),
]

nitpick_ignore_regex = [
    ('py:class', r'elementpath\.datatypes\..*'),
    ('py:class', r'collections\.abc\..*'),
    ('py:class', r'xmlschema\.validators\.validation\.(ST|DT)'),
    ('py:class', r'xmlschema\.namespaces\.(T|CT)'),
    ('py:class', r'elementpath\.protocols\..*Protocol'),
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'xmlschema'
copyright = '2016-2025, SISSA - Scuola Internazionale Superiore di Studi Avanzati'
author = 'Davide Brunato'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = '4.1'
# The full version, including alpha/beta/rc tags.
release = '4.1.0'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
# language = None
language = 'en'  # required by Sphinx v5.0.0

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = 'alabaster'
html_theme = 'sphinx_rtd_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']
html_static_path = []

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# This is required for the alabaster theme
# refs: http://alabaster.readthedocs.io/en/latest/installation.html#sidebars
html_sidebars = {
    '**': [
        'relations.html',  # needs 'show_related': True theme option to display
        'searchbox.html',
    ]
}


# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'xmlschemadoc'


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'xmlschema.tex', 'xmlschema Documentation',
     'Davide Brunato', 'manual'),
]

latex_appendices = ['api']
