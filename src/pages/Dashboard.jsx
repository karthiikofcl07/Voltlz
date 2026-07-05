import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { VoltApi } from '../api.js';
import { BatteryGauge, RiskPill, StatCard } from '../components/StatCard.jsx';
import { MapPanel } from '../components/MapPanel.jsx';
import { LineChart } from '../components/Charts.jsx';
import { useAuth } from '../context/AuthContext.jsx';

export default function Dashboard() {
  const { user } = useAuth();
  const [trip, setTrip] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  useEffect(() => {
    Promise.all([VoltApi.history(), VoltApi.analytics()]).then(([h, a]) => {
      setTrip(h.trips[0]);
      setAnalytics(a);
    });
  }, []);

  return (
    <div className="page-grid dashboard-grid">
      <section className="welcome-panel">
        <div>
          <p className="eyebrow">Good morning, {user?.name?.split(' ')[0] || 'Driver'}</p>
          <h1>Plan smarter. Drive farther.</h1>
          <p>AI-powered trip planning with optimized charging recommendations across Indian EV networks.</p>
          <Link to="/plan" className="primary-btn">Plan your trip</Link>
        </div>
        <div className="hero-vehicle-card">
          <span>Digital Twin</span>
          <strong>{trip?.vehicle_model || 'Tata Nexon EV Max'}</strong>
          <small>Live efficiency profile enabled</small>
        </div>
      </section>

      <div className="stat-strip">
        <StatCard label="Estimated Range" value={`${trip?.prediction?.range_km || 317} km`} sub="Hybrid ML + physics" />
        <StatCard label="Today's Savings" value={`₹${analytics?.total_savings_inr || 2432}`} sub="vs petrol" tone="amber" />
        <StatCard label="CO₂ Saved" value={`${analytics?.co2_saved_kg || 46.8} kg`} sub="this month" tone="cyan" />
        <StatCard label="Eco Score" value={`${analytics?.eco_score || 86}/100`} sub="efficient" />
      </div>

      <section className="panel large-map">
        <div className="panel-head">
          <div><p className="eyebrow">Latest route</p><h2>{trip ? `${trip.origin.split(',')[0]} to ${trip.destination.split(',')[0]}` : 'Delhi to Manali'}</h2></div>
          {trip && <RiskPill level={trip.risk.level} />}
        </div>
        <MapPanel trip={trip} />
      </section>

      <section className="panel">
        <div className="panel-head"><h2>Battery Health</h2><Link to="/vehicle">Details</Link></div>
        <BatteryGauge value={92} label="State of health" />
        <div className="battery-list">
          <span>Estimated capacity <b>37.1 kWh</b></span>
          <span>Cycle count <b>512</b></span>
          <span>Fast-charge ratio <b>32%</b></span>
        </div>
      </section>

      <section className="panel">
        <div className="panel-head"><h2>Energy Curve</h2><Link to="/analytics">Analytics</Link></div>
        <div className="chart-box"><LineChart rows={trip?.analytics?.energy_series || []} /></div>
      </section>

      <section className="panel">
        <div className="panel-head"><h2>AI Suggestion</h2><Link to="/assistant">Ask</Link></div>
        <p className="assistant-note">{trip?.assistant_summary || 'Plan a route to receive charger and cost recommendations.'}</p>
      </section>
    </div>
  );
}
