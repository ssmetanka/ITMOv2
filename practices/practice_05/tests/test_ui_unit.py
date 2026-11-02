import os
import subprocess
import sys
import unittest
from pathlib import Path
from shutil import which


class TestUIUnit(unittest.TestCase):
    def test_node_tests(self):
        if which('node') is None:
            self.skipTest('Node.js not available')
        # Collect .mjs tests explicitly to avoid shell globbing assumptions
        tests_dir = Path(__file__).resolve().parent.parent / 'ui' / 'tests'
        test_files = sorted(str(p) for p in tests_dir.glob('*.test.mjs'))
        cmd = ['node', '--test', *test_files]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        self.assertEqual(proc.returncode, 0, msg=proc.stdout)
