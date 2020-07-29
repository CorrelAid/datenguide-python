.. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/CorrelAid/datenguide-python/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

Datenguide Python could always use more documentation, whether as part of the
official Datenguide Python docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/CorrelAid/datenguide-python/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `datenguide-python` for local development.

1. Fork the `datenguide-python` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/datenguide-python.git

3. Install your local copy into a virtualenv. Assuming you have virtualenvwrapper installed, this is how you set up your fork for local development::

    $ mkvirtualenv datenguide-python
    $ cd datenguide-python/
    $ python setup.py develop

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass flake8 and the
   tests, including testing other Python versions with tox::

    $ flake8 datenguidepy tests
    $ tox

   To get flake8 and tox, just pip install them into your virtualenv.

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

Quality Assurance Guidelines
----------------------------

In order to contribute code, it has to pass certain automatic checks.
When a pull request is submitted these checks will run with travis-ci.
To ensure in advance that the that these are likely to pass developers
are highly encouraged to use following tools. tox and pre-commit.
Both are described in the next sections.

tox
~~~

tox sets up envrionments and runs quality checks for them. These include
tests and other tools for quality insurance. The configuration
is given in the ``tox.ini`` and by default the package is checked agains
python 3.6, 3.7 and 3.8 environments. To execute the checks simply run
>>> tox


pre-commit
~~~~~~~~~~

pre-commit is a python package that helps with the setup of git pre-commit hooks.
The git pre-commit hooks will run quality assurance checks whenever a commit is made.


The project comes with a pre-commit configuration file. In order to set it up locally
run
>>> pre-commit install
>>> pre-commit run --all-files

This will setup the hooks and install the dependencies. Subsequent runs will therefore
be faster.





Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. The pull request should work for Python  3.6, 3.7, 3.8 and for PyPy. Check
   https://travis-ci.org/CorrelAid/datenguide-python/pull_requests
   and make sure that the tests pass for all supported Python versions.



Deploying
---------

A reminder for the maintainers on how to deploy.
Make sure all your changes are committed (including an entry in HISTORY.rst).
Update the datenguidepy/VERSION file and increase the package version.
Make sure all tox/travis-ci tests are passing and then deplot manually using
CorrelAid's Pypi credentials and the commands::

$python setup.py sdist
$twine dist/<new_sdist_version>