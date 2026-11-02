import io
import json
import subprocess
import sys
import unittest


class TestMCPDiffGuard(unittest.TestCase):
    def setUp(self):
        self.proc = subprocess.Popen([
            sys.executable, 'mcp_server/server.py'
        ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def tearDown(self):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=2)
            except Exception:
                self.proc.kill()

    def _rpc(self, obj):
        line = json.dumps(obj)
        self.proc.stdin.write(line + "\n")
        self.proc.stdin.flush()
        out = self.proc.stdout.readline()
        return json.loads(out)

    def test_handshake_and_tools(self):
        resp = self._rpc({"jsonrpc":"2.0","id":1,"method":"initialize","params":{}})
        self.assertEqual(resp.get('id'), 1)
        self.assertIn('result', resp)
        resp = self._rpc({"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}})
        tools = resp['result']['tools']
        names = [t['name'] for t in tools]
        self.assertIn('validate_diff_stats', names)

    def test_validate_diff_stats_outcomes(self):
        # Accepted
        resp = self._rpc({
            "jsonrpc":"2.0","id":3,"method":"tools/call","params":{
                "name":"validate_diff_stats","arguments":{"diff_text":"+ ok\n"}
            }
        })
        content = resp['result']['content'][0]['text']
        result = json.loads(content)
        self.assertEqual(result['status'], 'ACCEPTED')

        # Rejected by lines
        resp = self._rpc({
            "jsonrpc":"2.0","id":4,"method":"tools/call","params":{
                "name":"validate_diff_stats","arguments":{"diff_text":"+ x\n"*301}
            }
        })
        result = json.loads(resp['result']['content'][0]['text'])
        self.assertEqual(result['status'], 'REJECTED')

        # Invalid input
        resp = self._rpc({
            "jsonrpc":"2.0","id":5,"method":"tools/call","params":{
                "name":"validate_diff_stats","arguments":{"diff_text":123}
            }
        })
        result = json.loads(resp['result']['content'][0]['text'])
        self.assertEqual(result['status'], 'INVALID_INPUT')
