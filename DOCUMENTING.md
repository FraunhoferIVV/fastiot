# Guidelines for documenting fastIoT

## Principles

* Documentation should stay closely to the code, no external documentation of e.g. variables
* How-Tos describe the general way of doing things and reference to the used libraries, data models, …
* How-Tos may be either written in ReStructed Text (`.rst`-Files) or Markedly Structured Text (`.md`-Files)
* Docstrings need to be in RST at the moment
* Use direct references to typical Python objects as described in [Cross-referencing Python objects](https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html#cross-referencing-python-objects)
* A service should contain it’s docstring in the `__init__.py` including a reference configuration, if needed

## Some hints on documenting with Sphinx

* You can find hints on the syntax for [Markdown](https://myst-parser.readthedocs.io) or [RST](https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html)
* Environment Variables can also be marked as reference, use ~~~.. envvar::`MY_ENV_VAR`~~~ 
* Mark new additions with `.. versionadded::`

## Building the documentation

1. You can either install as a Linux package or with pip.
  - Under the `docs` you will find the `sphinx-requirements.txt` to be installed in your local venv
  - See [Installing Sphinx](https://www.sphinx-doc.org/en/master/usage/installation.html) for more information about sphinx.
2. Modify the .rst-files inside the `source` directory to your liking. There is a [primer on formatting with reStructuredText](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html) in the Sphinx documentation.
3. Build the documentation inside the `source` directory with `./make_docs.sh`