export const initialState = {
  status: 'idle',
  limits: { max_lines: 300, max_chars: 10000 },
  input: '',
  history: [],
};

export function countMetrics(text) {
  // Count chars like JS String.length (UTF-16 code units); native length suffices
  const chars = text.length;
  const lines = text.trim().length ? text.trim().split(/\r?\n/).length : 0;
  return { chars, lines };
}

export function reducer(state, action) {
  switch (action.type) {
    case 'set_limits':
      return { ...state, limits: action.limits };
    case 'input': {
      const input = action.value;
      const { lines, chars } = countMetrics(input);
      let status = 'idle';
      if (!input.trim()) status = 'validation_error';
      if (lines > state.limits.max_lines || chars > state.limits.max_chars) status = 'validation_error';
      return { ...state, input, status };
    }
    case 'loading':
      return { ...state, status: 'loading' };
    case 'success':
      return { ...state, status: 'success', history: [action.record, ...state.history].slice(0, 5) };
    case 'llm_unavailable':
      return { ...state, status: 'llm_unavailable' };
    case 'network_error':
      return { ...state, status: 'network_error' };
    default:
      return state;
  }
}
