#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# FastIoT documentation build configuration file
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

import os
import sys
from datetime import datetime

project_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Include src dir if not already included
_python_src_dir = os.path.join(project_root_dir, 'src')
if _python_src_dir not in sys.path:
    sys.path.append(_python_src_dir)

from fastiot import __version__

# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.autosummary',
              'sphinx.ext.viewcode',
              'sphinx.ext.coverage',
              'sphinx_automodapi.automodapi',
              'sphinx_autodoc_typehints',
              'sphinx.ext.autosectionlabel',
              'myst_parser',
              'sphinxcontrib.autodoc_pydantic'
              ]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['templates']
autodoc_member_order = 'bysource'
numpydoc_show_class_members = False
autosectionlabel_prefix_document = True

cmd_line_template = "sphinx-apidoc --module-first -f -o {outputdir} {moduledir}"

coverage_show_missing_items = True

autodoc_pydantic_model_show_json = False
autodoc_pydantic_model_show_config = False
autodoc_pydantic_model_show_field_summary = False
# If true, `todo` and `todoList` produce output, else they produce nothing.
autosummary_generate = True
# May be extended by also using 'special-members',
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}
# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = {
    '.rst': 'restructuredtext',
}
# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'FastIoT'
copyright = f'2022-{datetime.now().year}, Fraunhofer IVV, Dresden'
author = 'IVV-DD'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = __version__
# The full version, including alpha/beta/rc tags.
release = __version__

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = 'en'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
##
if not os.getenv('FASTIOT_DOCSTYLE_READTHEDOCS'):
    html_theme = 'sphinx_material'
    html_theme_options = {'color_primary': 'teal', 'color_accent': 'orange'}

else:
    html_theme = 'sphinx_rtd_theme'
    html_theme_options = {'titles_only': False}

show_related = True

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['static']
html_sidebars = {
    "**": ["logo-text.html", "globaltoc.html", "localtoc.html", "searchbox.html"]
}
html_css_files = [
    'fastiot.css',
]

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# This is required for the alabaster theme
# refs: http://alabaster.readthedocs.io/en/latest/installation.html#sidebars
#html_sidebars = {
#    '**': [
#        'relations.html',  # needs 'show_related': True theme option to display
#        'searchbox.html',
#    ]
#}


# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'fastiotdoc'
