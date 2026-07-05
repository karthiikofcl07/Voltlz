import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Brand } from '../components/Brand.jsx';
import { useAuth } from '../context/AuthContext.jsx';

export default function Login() {
  const { login, register } = useAuth();
  const navigate = useNavigate();
  const [mode, setMode] = useState('login');
  const [form, setForm] = useState({ name: 'Arjun Mehta', email: 'arjun@voltnav.demo', password: 'voltnav123' });
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError('');
    try {
      if (mode === 'login') await login(form.email, form.password);
      else await register(form.name, form.email, form.password);
      navigate('/');
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="login-page">
      <Link to="/welcome" className="login-brand"><Brand /></Link>
      <div className="login-visual">
        <div className="aurora-card">
          <span>VoltNav 2.0</span>
          <h1>Route energy, charger availability and cost intelligence in one cockpit.</h1>
          <p>Demo account is pre-filled for judges and recruiters. You can also register a new account.</p>
        </div>
      </div>
      <form className="auth-card" onSubmit={submit}>
        <p className="eyebrow">{mode === 'login' ? 'Welcome back' : 'Create account'}</p>
        <h2>{mode === 'login' ? 'Sign in to VoltNav' : 'Start your EV profile'}</h2>
        {mode === 'register' && (
          <label>Full name<input value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} required /></label>
        )}
        <label>Email<input type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} required /></label>
        <label>Password<input type="password" value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} required minLength={6} /></label>
        {error && <div className="error-box">{error}</div>}
        <button className="primary-btn" disabled={busy}>{busy ? 'Authenticating...' : mode === 'login' ? 'Login' : 'Create account'}</button>
        <button type="button" className="ghost" onClick={() => setMode(mode === 'login' ? 'register' : 'login')}>
          {mode === 'login' ? 'Need a new account?' : 'Already have an account?'}
        </button>
      </form>
    </div>
  );
}
