acnutils
========
.. image:: https://img.shields.io/github/workflow/status/AntiCompositeNumber/AntiCompositeBot/Python%20application
    :alt: GitHub Workflow Status
    :target: https://github.com/AntiCompositeNumber/acnutils/actions
.. image:: https://coveralls.io/repos/github/AntiCompositeNumber/acnutils/badge.svg?branch=master
    :alt: Coverage status
    :target: https://coveralls.io/github/AntiCompositeNumber/acnutils?branch=master
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :alt: Code style: black
    :target: https://github.com/psf/black
.. image:: https://img.shields.io/pypi/pyversions/acnutils
    :alt: PyPI - Python Version
    :target: https://pypi.org/project/acnutils/


A collection of various scripts used by AntiCompositeNumber's bots.

Feel free to use this if you find it useful, however, no guarentees of stability are made.
Pull requests are welcome, but may be declined if they would not be useful for my bots or tools.

This package depends on pywikibot. Some utilites also require a database connection via the toolforge libarary, to enable those install ``acnutils[db]``.

Poetry is used for dependency management and package building. To set up this project, run ``poetry install -E db``.
