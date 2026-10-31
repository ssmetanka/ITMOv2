import assert from 'node:assert';
import { reducer, initialState } from '../state.js';

describe('state reducer', () => {
  it('disables on empty input', () => {
    let s = { ...initialState };
    s = reducer(s, { type: 'input', value: '   ' });
    assert.equal(s.status, 'validation_error');
  });
  it('success after submit', () => {
    let s = { ...initialState };
    s = reducer(s, { type: 'input', value: '+ ok' });
    s = reducer(s, { type: 'loading' });
    s = reducer(s, { type: 'success', record: { id: '1', created_at: 't', status: 'success', review: 'r' } });
    assert.equal(s.status, 'success');
    assert.equal(s.history.length, 1);
  });
});
