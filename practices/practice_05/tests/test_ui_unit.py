import os
import subprocess
import sys
import unittest


class TestUIUnit(unittest.TestCase):
    def test_node_tests(self):
        node = shutil.which('node') if False else None
        # Try to find node in PATH
        from shutil import which
        if which('node') is None:
            self.skipTest('Node.js not available')
        proc = subprocess.run(['node', '--test', 'ui/tests'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        self.assertEqual(proc.returncode, 0, msg=proc.stdout)
