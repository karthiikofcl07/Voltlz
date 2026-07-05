import { Link, NavLink } from 'react-router-dom';
import { Brand } from './Brand.jsx';
import { useAuth } from '../context/AuthContext.jsx';

const items = [
  ['/', 'Dashboard'],
  ['/plan', 'Plan Trip'],
  ['/chargers', 'Charging Stations'],
  ['/analytics', 'Analytics'],
  ['/vehicle', 'Battery Health'],
  ['/assistant', 'AI Assistant']
];

export function SideNav() {
  const { user, logout } = useAuth();
  return (
    <aside className="sidenav">
      <Link to="/" className="nav-brand"><Brand /></Link>
      <nav>
        {items.map(([to, label]) => (
          <NavLink key={to} to={to} end={to === '/'}>{label}</NavLink>
        ))}
      </nav>
      <div className="nav-user">
        <div className="avatar">{(user?.name || 'V').slice(0, 1)}</div>
        <div>
          <strong>{user?.name || 'VoltNav User'}</strong>
          <span>Premium driver</span>
        </div>
        <button onClick={logout} className="ghost tiny">Logout</button>
      </div>
    </aside>
  );
}

export function MobileTabs() {
  return (
    <nav className="mobile-tabs">
      {items.slice(0, 5).map(([to, label]) => (
        <NavLink key={to} to={to} end={to === '/'}>{label.split(' ')[0]}</NavLink>
      ))}
    </nav>
  );
}
