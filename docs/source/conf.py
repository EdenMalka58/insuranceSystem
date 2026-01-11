# Configuration file for the Sphinx documentation builder.

# -- Project information -----------------------------------------------------
import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

project = "Insurance System - Damage Inspector"
copyright = "2026, Eden Malka"
author = "Eden Malka"
release = "1.0"

# -- General configuration ---------------------------------------------------

extensions = [
    "myst_parser",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

templates_path = ["_templates"]

exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
]

# -- MyST configuration ------------------------------------------------------

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "html_admonition",
    "html_image",
]

myst_heading_anchors = 3

# -- Options for HTML output -------------------------------------------------

html_theme = "furo"

html_theme_options = {
    "collapse_navigation": False,
    "navigation_depth": 3,  
    "style_external_links": True,
}

html_static_path = ["_static"]

html_title = "Insurance System – Backend Documentation"

