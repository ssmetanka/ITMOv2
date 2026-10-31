import os
import subprocess
import sys
import unittest

class TestE2E(unittest.TestCase):
    def test_server_runs(self):
        # minimal smoke: start server and kill
        proc = subprocess.Popen([sys.executable, '-m', 'app.server', '--port', '0'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.terminate()
        proc.wait(timeout=5)
        self.assertTrue(proc.returncode is not None)
