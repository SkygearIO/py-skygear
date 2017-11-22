# -*- coding: utf-8 -*-
#
# -- General configuration -----------------------------------------------------

import sphinx_rtd_theme
import os
import sys
from pkg_resources import find_distributions
from email import message_from_string

directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..")
print(directory)
pkgInfo = next(find_distributions(directory)).get_metadata('PKG-INFO')
msg = message_from_string(pkgInfo)
version = msg['Version']
name = msg['Name']


sys.path.insert(0, '../')
source_suffix = '.rst'
master_doc = 'index'
html_use_index = True
project = name
copyright = u'Copyright 2017 Oursky Ltd'
extensions = ['sphinx.ext.autodoc', 'sphinxcontrib.napoleon']
exclude_patterns =['_build', 'test']
autodoc_member_order = 'bysource'
autoclass_content = 'both'
napoleon_google_docstring = True
autodoc_inherit_docstrings = False
# -- Options for HTML output ---------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
# -- HTML theme options for `dotted` style -------------------------------------

html_theme_options = {
}
