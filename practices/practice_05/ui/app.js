import { initialState, reducer, countMetrics } from './state.js';
import { createApi } from './api.js';

const api = createApi(window.fetch.bind(window));

let state = { ...initialState };

function render() {
  const counter = document.getElementById('counter');
  const { lines, chars } = countMetrics(state.input);
  counter.textContent = `${lines} lines / ${chars} chars`;
  counter.className = 'counter' + ((lines > state.limits.max_lines || chars > state.limits.max_chars) ? ' exceeded' : '');
  const btn = document.getElementById('check');
  btn.disabled = state.status === 'validation_error' || state.status === 'loading' || !state.input.trim();
  const statusEl = document.getElementById('status');
  statusEl.textContent = state.status;
  const ul = document.getElementById('history');
  ul.innerHTML = '';
  state.history.forEach(r => {
    const li = document.createElement('li');
    li.textContent = `${r.created_at} — ${r.review}`;
    li.addEventListener('click', async () => {
      try {
        // simple display of selected review
        alert(r.review);
      } catch {}
    });
    ul.appendChild(li);
  });
}

async function init() {
  try {
    const lim = await api.limits();
    state = reducer(state, { type: 'set_limits', limits: lim });
  } catch {}
  try {
    const hist = await api.list(5);
    if (hist && Array.isArray(hist.items)) {
      // preload recent history
      state.history = hist.items.slice(0, 5);
    }
  } catch {}
  render();
}

document.addEventListener('DOMContentLoaded', () => {
  const ta = document.getElementById('diff');
  const btn = document.getElementById('check');
  ta.addEventListener('input', (e) => {
    state = reducer(state, { type: 'input', value: e.target.value });
    render();
  });
  ta.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') submit();
  });
  btn.addEventListener('click', submit);
  init();
});

async function submit() {
  state = reducer(state, { type: 'loading' });
  render();
  try {
    const res = await api.createReview(state.input);
    if (res.error) {
      if (res.error.code === 'LLM_UNAVAILABLE') state = reducer(state, { type: 'llm_unavailable' });
      else state = reducer(state, { type: 'validation_error' });
    } else {
      state = reducer(state, { type: 'success', record: res });
    }
  } catch {
    state = reducer(state, { type: 'network_error' });
  }
  render();
}
