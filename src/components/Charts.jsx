import { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';

export function LineChart({ rows = [], label = 'Energy consumption' }) {
  const ref = useRef(null);
  useEffect(() => {
    if (!ref.current) return;
    const chart = new Chart(ref.current, {
      type: 'line',
      data: {
        labels: rows.map(r => r.label),
        datasets: [{
          label,
          data: rows.map(r => r.consumption || r.km || r.savings || 0),
          borderColor: '#36f69a',
          backgroundColor: 'rgba(54,246,154,.14)',
          fill: true,
          tension: 0.42,
          pointRadius: 3
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { color: '#9fb6c3' }, grid: { color: 'rgba(255,255,255,.04)' } },
          y: { ticks: { color: '#9fb6c3' }, grid: { color: 'rgba(255,255,255,.06)' } }
        }
      }
    });
    return () => chart.destroy();
  }, [rows, label]);
  return <canvas ref={ref} />;
}

export function Donut({ values = { Fast: 62, Home: 25, Destination: 13 } }) {
  const total = Object.values(values).reduce((a, b) => a + b, 0);
  let start = 0;
  const colors = ['#36f69a', '#4cc9ff', '#ffd267', '#2777ff'];
  const segments = Object.entries(values).map(([key, value], index) => {
    const pct = value / total;
    const dash = `${pct * 100} ${100 - pct * 100}`;
    const rotate = start * 360;
    start += pct;
    return <circle key={key} r="15.9" cx="18" cy="18" fill="transparent" stroke={colors[index]} strokeWidth="4.2" strokeDasharray={dash} strokeDashoffset="25" transform={`rotate(${rotate} 18 18)`} />;
  });
  return (
    <div className="donut-wrap">
      <svg viewBox="0 0 36 36">{segments}</svg>
      <div>{Object.entries(values).map(([k, v]) => <span key={k}>{k}: {v}%</span>)}</div>
    </div>
  );
}
