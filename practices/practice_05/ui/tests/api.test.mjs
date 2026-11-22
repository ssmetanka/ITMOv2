import assert from 'node:assert';
import { describe, it } from 'node:test';
import { createApi } from '../api.js';

function makeFetch(resps) {
  return async (url, opts={}) => {
    const key = (opts.method || 'GET') + ' ' + url;
    const r = resps[key];
    return {
      ok: r.status>=200 && r.status<300,
      status: r.status,
      async json(){ return r.body },
    };
  };
}

describe('api client', () => {
  it('limits', async () => {
    const api = createApi(makeFetch({ 'GET /api/limits': { status: 200, body: { max_lines: 300, max_chars: 10000 } } }));
    const lim = await api.limits();
    assert.equal(lim.max_lines, 300);
  });
  it('llm unavailable', async () => {
    const api = createApi(makeFetch({ 'POST /api/reviews': { status: 504, body: {} } }));
    const res = await api.createReview('x');
    assert.equal(res.error.code, 'LLM_UNAVAILABLE');
  });
});
