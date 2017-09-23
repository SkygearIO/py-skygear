# -*- coding: utf-8 -*-
#
# -- General configuration -----------------------------------------------------

import sphinx_rtd_theme
import os
import sys

sys.path.insert(0, '../')
source_suffix = '.rst'
master_doc = 'index'
html_use_index = True
project = u'py-skygear'
copyright = u'Copyright 2017 Oursky Ltd'
extensions = ['sphinx.ext.autodoc', 'sphinxcontrib.napoleon']
exclude_patterns =['_build', 'test']
autodoc_member_order = 'bysource'
autoclass_content = 'both'
version = '1.0.0'
napoleon_google_docstring = True
# -- Options for HTML output ---------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
# -- HTML theme options for `dotted` style -------------------------------------

html_theme_options = {
}
