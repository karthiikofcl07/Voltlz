import { useEffect, useState } from 'react';
import { VoltApi } from '../api.js';
import { Donut, LineChart } from '../components/Charts.jsx';
import { StatCard } from '../components/StatCard.jsx';

export default function Analytics() {
  const [data, setData] = useState(null);
  useEffect(() => { VoltApi.analytics().then(setData); }, []);
  const rows = data?.monthly?.map(r => ({ label: r.label, consumption: r.savings })) || [];
  return (
    <div className="analytics-layout">
      <section className="panel wide">
        <div className="panel-head"><div><p className="eyebrow">Analytics</p><h2>Sustainability and cost dashboard</h2></div><span>This month</span></div>
        <div className="stat-strip">
          <StatCard label="Distance" value={`${data?.total_distance_km || 0} km`} sub="tracked" />
          <StatCard label="Savings" value={`₹${data?.total_savings_inr || 0}`} sub="vs petrol" tone="amber" />
          <StatCard label="CO₂ saved" value={`${data?.co2_saved_kg || 0} kg`} sub="tailpipe avoided" tone="cyan" />
          <StatCard label="Eco Score" value={`${data?.eco_score || 86}/100`} sub="sustainable" />
        </div>
        <div className="chart-box tall"><LineChart rows={rows} label="Weekly savings" /></div>
      </section>
      <section className="panel">
        <div className="panel-head"><h2>Cost breakdown</h2></div>
        <Donut values={data?.charger_mix} />
      </section>
      <section className="panel">
        <div className="panel-head"><h2>Carbon dashboard</h2></div>
        <div className="carbon-card">
          <strong>{data?.co2_saved_kg || 0} kg</strong>
          <span>Estimated CO₂ reduction from EV travel versus petrol baseline.</span>
          <b>{Math.round((data?.co2_saved_kg || 0) / 21.7)} trees equivalent</b>
        </div>
      </section>
      <section className="panel">
        <div className="panel-head"><h2>Trip operations</h2></div>
        <div className="detail-grid">
          <span>Total trips <b>{data?.trip_count || 0}</b></span>
          <span>Charging time <b>{data?.total_charging_time || '0m'}</b></span>
          <span>Avg cost saved <b>₹{data ? Math.round(data.total_savings_inr / Math.max(1, data.trip_count)) : 0}</b></span>
          <span>Fleet-ready <b>Yes</b></span>
        </div>
      </section>
    </div>
  );
}
