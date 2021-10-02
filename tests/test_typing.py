#!/usr/bin/env python
#
# Copyright (c), 2018-2020, SISSA (International School for Advanced Studies).
# All rights reserved.
# This file is distributed under the terms of the MIT License.
# See the file 'LICENSE' in the root directory of the present
# distribution, or http://opensource.org/licenses/MIT.
#
# @author Davide Brunato <brunato@sissa.it>
#
"""Tests about static typing of xmlschema objects."""

import unittest
import subprocess
import re
from pathlib import Path

try:
    import mypy
except ImportError:
    mypy = None


@unittest.skipIf(mypy is None, "mypy is not installed")
class TestTyping(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cases_dir = Path(__file__).parent.joinpath('test_cases/mypy')
        cls.error_pattern = re.compile(r'Found \d+ error', re.IGNORECASE)

    def check_mypy_output(self, testfile, *options):
        cmd = ['mypy', testfile]
        if options:
            cmd.extend(str(opt) for opt in options)
        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        self.assertEqual(process.stderr, b'')
        output = process.stdout.decode('utf-8').strip()
        output_lines = output.split('\n')

        self.assertGreater(len(output_lines), 0, msg=output)
        self.assertNotRegex(output_lines[-1], self.error_pattern, msg=output)
        return output_lines

    def test_strict_simple_types(self):
        case_path = self.cases_dir.joinpath('strict/simple_types.py')
        output_lines = self.check_mypy_output(case_path, '--strict')
        self.assertTrue(output_lines[0].startswith('Success:'), msg='\n'.join(output_lines))

    def test_reveal_simple_type_restriction1(self):
        case_path = self.cases_dir.joinpath('reveal/simple_type_restriction1.py')
        output_lines = self.check_mypy_output(case_path)
        for line in output_lines:
            self.assertIn(': note: Revealed type is', line)

        self.assertIn('is "Any"', output_lines[0])
        self.assertIn('XsdAtomicRestriction', output_lines[1])
        self.assertIn('Union[', output_lines[2])
        self.assertIn('XsdMinExclusiveFacet', output_lines[2])
        self.assertIn('"Union[builtins.int, None]"', output_lines[3])
        self.assertIn('"Union[builtins.int, None]"', output_lines[4])


if __name__ == '__main__':
    unittest.main()
