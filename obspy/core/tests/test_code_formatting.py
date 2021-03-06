# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from future.builtins import *  # NOQA @UnusedWildImport

import codecs
import fnmatch
import os
import re
import unittest

from obspy.core.util.testing import check_flake8, get_all_py_files


def _match_exceptions(filename, exceptions):
    for pattern in exceptions:
        if fnmatch.fnmatch(filename, pattern):
            return True
    return False


class CodeFormattingTestCase(unittest.TestCase):
    """
    Test codebase for compliance with the flake8 tool.
    """
    @unittest.skipIf('OBSPY_NO_FLAKE8' in os.environ, 'flake8 check disabled')
    def test_flake8(self):
        """
        Test codebase for compliance with the flake8 tool.
        """
        report, message = check_flake8()
        file_count = report.counters["files"]
        error_count = report.get_count()
        self.assertGreater(file_count, 10)
        self.assertEqual(error_count, 0, "\n" + message.decode())

    def test_use_obspy_deprecation_warning(self):
        """
        Tests that ObsPyDeprecationWarning is used rather than the usual
        DeprecationWarning when using `warnings.warn()`
        (because the latter is not shown by Python by default anymore).
        """
        msg = ("File '%s' seems to use DeprecationWarning instead of "
               "obspy.core.util.deprecation_helpers.ObsPyDeprecationWarning:"
               "\n\n%s")
        pattern = r'warn\([^)]*?([\w]*?)DeprecationWarning[^)]*\)'

        failures = []
        for filename in get_all_py_files():
            with codecs.open(filename, "r", encoding="utf-8") as fh:
                content = fh.read()

            for match in re.finditer(pattern, content):
                if match.group(1) != 'ObsPy':
                    failures.append(msg % (filename, match.group(0)))

        self.assertEqual(len(failures), 0, "\n" + "\n".join(failures))


class FutureUsageTestCase(unittest.TestCase):
    def test_future_imports_in_every_file(self):
        """
        Tests that every single Python file includes the appropriate future
        headers to enforce consistent behavior.
        """
        # There are currently only three exceptions. Two files are imported
        # during installation and thus cannot contain future imports. The
        # third file is the compatibility layer which naturally also does
        # not want to import future.
        exceptions = [
            os.path.join('core', 'util', 'libnames.py'),
            os.path.join('core', 'util', 'version.py'),
            os.path.join('core', 'compatibility.py'),
            os.path.join('lib', '*'),
        ]
        exceptions = [os.path.join("*", "obspy", i) for i in exceptions]

        future_import_line = (
            "from __future__ import (absolute_import, division, "
            "print_function, unicode_literals)")
        builtins_line = "from future.builtins import *  # NOQA"

        future_imports_pattern = re.compile(
            r"^from __future__ import \(absolute_import,\s*"
            r"division,\s*print_function,\s*unicode_literals\)$",
            flags=re.MULTILINE)

        builtin_pattern = re.compile(
            r"^from future\.builtins import \*  # NOQA",
            flags=re.MULTILINE)

        failures = []
        for filename in get_all_py_files():
            if _match_exceptions(filename, exceptions):
                continue
            with codecs.open(filename, "r", encoding="utf-8") as fh:
                content = fh.read()

            if re.search(future_imports_pattern, content) is None:
                failures.append("File '%s' misses imports: %s" %
                                (filename, future_import_line))

            if re.search(builtin_pattern, content) is None:
                failures.append("File '%s' misses imports: %s" %
                                (filename, builtins_line))
        self.assertEqual(len(failures), 0, "\n" + "\n".join(failures))


class MatplotlibBackendUsageTestCase(unittest.TestCase):
    def test_no_pyplot_import_in_any_file(self):
        """
        Tests that no Python file spoils matplotlib backend switching by
        importing e.g. `matplotlib.pyplot` (not enclosed in a def/class
        statement).
        """
        patterns = (
            r"(?<!# )from pylab\..*? import",
            r"(?<!# )import pylab",
            r"(?<!# )from matplotlib import (pyplot)|(backends)",
            r"(?<!# )import matplotlib\.(pyplot)|(backends)",
            )
        msg = ("File '{}' (line {})\nmatches a forbidden matplotlib import "
               "statement outside of class/def statements\n(breaking "
               "matplotlib backend switching on some systems):\n    '{}'")
        exceptions = [
            os.path.join('io', 'css', 'contrib', 'css28fix.py'),
            os.path.join('*', 'tests', '*'),
            os.path.join('*', '*', 'tests', '*'),
        ]
        exceptions = [os.path.join("*", "obspy", i) for i in exceptions]

        failures = []
        for filename in get_all_py_files():
            if _match_exceptions(filename, exceptions):
                continue
            line_number = 1
            in_docstring = False
            with codecs.open(filename, "r", encoding="utf-8") as fh:
                line = fh.readline()
                while line:
                    # detect start/end of docstring
                    if re.match(r"['\"]{3}", line):
                        in_docstring = not in_docstring
                    # skip if inside docstring
                    if not in_docstring:
                        # stop searching at first unindented class/def
                        if re.match(r"(class)|(def) ", line):
                            break
                        for pattern in patterns:
                            if re.search(pattern, line):
                                failures.append(msg.format(
                                    filename, line_number, line.rstrip()))
                    line = fh.readline()
                    line_number += 1
        self.assertEqual(len(failures), 0, "\n" + "\n\n".join(failures))


def suite():

    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CodeFormattingTestCase, 'test'))
    suite.addTest(unittest.makeSuite(FutureUsageTestCase, 'test'))
    suite.addTest(unittest.makeSuite(MatplotlibBackendUsageTestCase, 'test'))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
