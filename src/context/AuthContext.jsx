import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { AuthApi } from '../api.js';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('voltnav_token');
    if (!token) {
      setLoading(false);
      return;
    }
    AuthApi.me()
      .then(data => setUser(data.user))
      .catch(() => localStorage.removeItem('voltnav_token'))
      .finally(() => setLoading(false));
  }, []);

  const value = useMemo(() => ({
    user,
    loading,
    async login(email, password) {
      const data = await AuthApi.login({ email, password });
      localStorage.setItem('voltnav_token', data.token);
      setUser(data.user);
      return data.user;
    },
    async register(name, email, password) {
      const data = await AuthApi.register({ name, email, password });
      localStorage.setItem('voltnav_token', data.token);
      setUser(data.user);
      return data.user;
    },
    logout() {
      localStorage.removeItem('voltnav_token');
      setUser(null);
    }
  }), [user, loading]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
