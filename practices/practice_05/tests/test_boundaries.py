import json
import unittest
from http.client import HTTPConnection
from app.server import serve
from app.reviewer import ReviewService


class TestBoundaries(unittest.TestCase):
    def setUp(self):
        self.server, self.thread = serve(0)
        self.port = self.server.server_address[1]

    def tearDown(self):
        self.server.shutdown()

    def _conn(self):
        return HTTPConnection('127.0.0.1', self.port, timeout=3)

    def test_lines_300_ok_301_reject(self):
        c = self._conn()
        diff300 = ('+ ok\n' * 300)
        c.request('POST', '/api/reviews', body=json.dumps({'diff': diff300}))
        r = c.getresponse(); self.assertEqual(r.status, 200, r.read())
        r.read()

        c = self._conn()
        diff301 = ('+ ok\n' * 301)
        c.request('POST', '/api/reviews', body=json.dumps({'diff': diff301}))
        r = c.getresponse(); self.assertEqual(r.status, 422)
        r.read()

    def test_chars_10000_ok_10001_reject_ascii(self):
        c = self._conn()
        diff_ok = '+' + ('a' * 9999)
        c.request('POST', '/api/reviews', body=json.dumps({'diff': diff_ok}))
        r = c.getresponse(); self.assertEqual(r.status, 200, r.read())
        r.read()

        c = self._conn()
        diff_bad = '+' + ('a' * 10000)
        c.request('POST', '/api/reviews', body=json.dumps({'diff': diff_bad}))
        r = c.getresponse(); self.assertEqual(r.status, 422)
        r.read()

    def test_unicode_surrogate_pairs_count(self):
        # 😀 is 2 UTF-16 code units; 5000 of them = 10000, accepted; 5001 -> reject
        face = '😀'
        ok = face * 5000
        bad = face * 5001
        svc = ReviewService()
        svc.review_code(ok)  # should not raise
        with self.assertRaises(Exception):
            svc.review_code(bad)

    def test_crlf_is_counted_as_single_line(self):
        c = self._conn()
        diff = '+ a\r\n+ b\r\n'
        c.request('POST', '/api/reviews', body=json.dumps({'diff': diff}))
        r = c.getresponse(); self.assertEqual(r.status, 200, r.read())
        r.read()
