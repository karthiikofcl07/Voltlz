const API_BASE = import.meta.env.VITE_API_BASE || '/api';

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

export async function api(path, options = {}) {
  const token = localStorage.getItem('voltnav_token');
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };
  if (token) headers.Authorization = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    let detail = 'Request failed';
    try {
      detail = (await res.json()).detail || detail;
    } catch {
      detail = res.statusText;
    }
    throw new ApiError(detail, res.status);
  }
  if (options.raw) return res;
  return res.json();
}

export const AuthApi = {
  login: payload => api('/auth/login', { method: 'POST', body: JSON.stringify(payload) }),
  register: payload => api('/auth/register', { method: 'POST', body: JSON.stringify(payload) }),
  me: () => api('/me')
};

export const VoltApi = {
  meta: () => api('/meta'),
  planTrip: payload => api('/trips/plan', { method: 'POST', body: JSON.stringify(payload) }),
  history: () => api('/trips/history'),
  chargers: (q = '') => api(`/chargers/search?q=${encodeURIComponent(q)}`),
  analytics: () => api('/analytics/summary'),
  assistant: payload => api('/assistant/chat', { method: 'POST', body: JSON.stringify(payload) }),
  vehicle: payload => api('/vehicles/profile', { method: 'POST', body: JSON.stringify(payload) }),
  pdfUrl: id => `${API_BASE}/trips/${id}/pdf`
};
