export function createApi(fetchImpl) {
  return {
    async limits() {
      const res = await fetchImpl('/api/limits');
      if (!res.ok) throw new Error('network');
      return res.json();
    },
    async createReview(diff) {
      const res = await fetchImpl('/api/reviews', { method: 'POST', body: JSON.stringify({ diff }) });
      if (res.status === 504) return { error: { code: 'LLM_UNAVAILABLE' } };
      if (res.status === 422) return { error: await res.json().then(x => x.error) };
      if (!res.ok) throw new Error('network');
      return res.json();
    },
    async list(limit = 5) {
      const res = await fetchImpl(`/api/reviews?limit=${limit}`);
      if (!res.ok) throw new Error('network');
      return res.json();
    }
  };
}
