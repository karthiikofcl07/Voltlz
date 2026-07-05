export function StatCard({ label, value, sub, tone = 'mint' }) {
  return (
    <article className={`stat-card tone-${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{sub}</small>
    </article>
  );
}

export function BatteryGauge({ value = 80, label = 'Battery at start' }) {
  const pct = Math.max(0, Math.min(100, Number(value)));
  return (
    <div className="battery-gauge" style={{ '--pct': `${pct}%` }}>
      <div className="ring"><b>{Math.round(pct)}%</b></div>
      <span>{label}</span>
    </div>
  );
}

export function RiskPill({ level }) {
  return <span className={`risk risk-${String(level || 'Safe').toLowerCase()}`}>{level}</span>;
}
