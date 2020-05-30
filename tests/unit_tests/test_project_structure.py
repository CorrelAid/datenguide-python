import os
import datenguidepy.query_builder


def test_project_structure():
    """Test package loading in tox.

    The package struture has an issue in combination
    with tox and pytest. Tox packages and installs an sdist
    of the package, nevertheless when the tests are executed
    this installed package is shadowed by the (not installed)
    version of the package in the project folder. This happens
    because pytest dynamically adds paths to sys.path
    to run the test cases. The problem with this is that error
    in the MANIFEST.in are not caught when modules from the
    projects folder are used instead of the installd sdist.

    This testcase checks for a file in the module folder of query_builder.
    This file is NOT in the Manifest.in and should therefore not
    be found in a tox test.
    """
    mod_dir = os.path.dirname(os.path.abspath(datenguidepy.query_builder.__file__))
    test_file = "TEST_PROJECT_STRUCTURE"
    test_path = os.path.join(mod_dir, test_file)
    assert not os.path.isfile(test_path)
