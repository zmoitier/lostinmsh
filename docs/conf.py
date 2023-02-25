"""Config file for sphinx."""

try:
    import lostinmsh
except ImportError:
    import os
    import sys

    sys.path.insert(0, os.path.abspath("../"))

    import lostinmsh

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "lostinmsh"
copyright = f"2023, {lostinmsh.__author__}"
author = lostinmsh.__author__
release = lostinmsh.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**.ipynb_checkpoints"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# -- Extensions --------------------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "sphinx.ext.coverage",
    "sphinx.ext.githubpages",
    "sphinx_rtd_theme",
    "sphinx_copybutton",
    "nbsphinx",
]

nbsphinx_execute = "never"

# "sphinx.ext.linkcode",
# def linkcode_resolve(domain, info):
#     if domain != "py":
#         return None
#     if not info["module"]:
#         return None
#     filename = info["module"].replace(".", "/")
#     return f"https://github.com/zmoitier/lostinmsh/{filename}.py"
