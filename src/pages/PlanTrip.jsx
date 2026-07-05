import { useEffect, useMemo, useState } from 'react';
import { VoltApi } from '../api.js';
import { BatteryGauge, RiskPill, StatCard } from '../components/StatCard.jsx';
import { MapPanel } from '../components/MapPanel.jsx';
import { LineChart } from '../components/Charts.jsx';

const defaultForm = {
  origin: 'Delhi, India',
  destination: 'Manali, Himachal Pradesh',
  departure_time: '2026-07-05T07:30:00',
  vehicle_model: 'Tata Nexon EV Max',
  battery_percent: 80,
  average_speed: 82,
  ambient_temp: 24,
  elevation_gain_m: 700,
  wind_speed: 12,
  humidity: 56,
  passenger_count: 2,
  cargo_weight_kg: 35,
  regen_efficiency: 0.18,
  tire_pressure_psi: 34,
  driving_style: 'Balanced',
  hvac_usage: 'Auto',
  road_type: 'Highway',
  traffic_density: 'Moderate',
  driving_mode: 'Safe',
  connector: 'CCS2',
  charger_priority: 'Balanced'
};

export default function PlanTrip() {
  const [meta, setMeta] = useState({ cities: [], vehicles: {} });
  const [form, setForm] = useState(defaultForm);
  const [trip, setTrip] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    VoltApi.meta().then(setMeta);
    VoltApi.history().then(h => setTrip(h.trips[0]));
  }, []);

  const vehicle = useMemo(() => meta.vehicles?.[form.vehicle_model], [meta, form.vehicle_model]);

  function update(name, value) {
    const numeric = ['battery_percent', 'average_speed', 'ambient_temp', 'elevation_gain_m', 'wind_speed', 'humidity', 'passenger_count', 'cargo_weight_kg', 'regen_efficiency', 'tire_pressure_psi'];
    setForm(prev => ({ ...prev, [name]: numeric.includes(name) ? Number(value) : value }));
  }

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError('');
    try {
      const planned = await VoltApi.planTrip(form);
      setTrip(planned);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  function downloadPdf() {
    const token = localStorage.getItem('voltnav_token');
    fetch(VoltApi.pdfUrl(trip.id), { headers: { Authorization: `Bearer ${token}` } })
      .then(res => res.blob())
      .then(blob => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `voltnav-trip-${trip.id}.pdf`;
        a.click();
        URL.revokeObjectURL(url);
      });
  }

  return (
    <div className="planner-layout">
      <form className="planner-form panel" onSubmit={submit}>
        <div className="panel-head"><div><p className="eyebrow">Plan your trip</p><h2>Energy-first route optimizer</h2></div></div>
        <div className="input-grid">
          <label>From<select value={form.origin} onChange={e => update('origin', e.target.value)}>{meta.cities.map(c => <option key={c}>{c}</option>)}</select></label>
          <label>To<select value={form.destination} onChange={e => update('destination', e.target.value)}>{meta.cities.map(c => <option key={c}>{c}</option>)}</select></label>
          <label>Departure<input type="datetime-local" value={form.departure_time} onChange={e => update('departure_time', e.target.value)} /></label>
          <label>Vehicle<select value={form.vehicle_model} onChange={e => update('vehicle_model', e.target.value)}>{Object.keys(meta.vehicles).map(v => <option key={v}>{v}</option>)}</select></label>
          <label>Battery at start<input type="range" min="10" max="100" value={form.battery_percent} onChange={e => update('battery_percent', e.target.value)} /><b>{form.battery_percent}%</b></label>
          <label>Average speed<input type="number" value={form.average_speed} onChange={e => update('average_speed', e.target.value)} /></label>
          <label>Ambient temp<input type="number" value={form.ambient_temp} onChange={e => update('ambient_temp', e.target.value)} /></label>
          <label>Elevation gain<input type="number" value={form.elevation_gain_m} onChange={e => update('elevation_gain_m', e.target.value)} /></label>
          <label>Passengers<input type="number" min="1" max="6" value={form.passenger_count} onChange={e => update('passenger_count', e.target.value)} /></label>
          <label>Cargo kg<input type="number" value={form.cargo_weight_kg} onChange={e => update('cargo_weight_kg', e.target.value)} /></label>
          <label>Driving style<select value={form.driving_style} onChange={e => update('driving_style', e.target.value)}>{['Eco', 'Balanced', 'Aggressive'].map(x => <option key={x}>{x}</option>)}</select></label>
          <label>Traffic<select value={form.traffic_density} onChange={e => update('traffic_density', e.target.value)}>{['Light', 'Moderate', 'Heavy'].map(x => <option key={x}>{x}</option>)}</select></label>
        </div>
        <div className="mode-row">
          {['Safe', 'Balanced', 'Risky'].map(mode => <button type="button" key={mode} className={form.driving_mode === mode ? 'selected' : ''} onClick={() => update('driving_mode', mode)}>{mode}</button>)}
        </div>
        <div className="mode-row">
          {['Balanced', 'Fastest', 'Cheapest'].map(mode => <button type="button" key={mode} className={form.charger_priority === mode ? 'selected' : ''} onClick={() => update('charger_priority', mode)}>{mode}</button>)}
        </div>
        {error && <div className="error-box">{error}</div>}
        <button className="primary-btn" disabled={busy}>{busy ? 'Optimizing...' : 'Optimize route'}</button>
      </form>

      <section className="planner-map panel">
        <div className="panel-head">
          <div><p className="eyebrow">Trip overview</p><h2>{trip ? `${trip.origin.split(',')[0]} to ${trip.destination.split(',')[0]}` : 'Route preview'}</h2></div>
          {trip && <RiskPill level={trip.risk.level} />}
        </div>
        <MapPanel trip={trip} />
        {trip && (
          <div className="route-summary">
            <StatCard label="Distance" value={`${trip.distance_km} km`} sub="route distance" />
            <StatCard label="Total Time" value={trip.total_time} sub={`${trip.charging_time} charging`} tone="cyan" />
            <StatCard label="Stops" value={trip.recommended_stops.length} sub="optimized" />
            <StatCard label="Arrival" value={`${trip.arrival_battery_percent}%`} sub="battery" tone="amber" />
          </div>
        )}
      </section>

      {trip && (
        <section className="panel planner-details">
          <div className="panel-head"><h2>Charging strategy</h2><button onClick={downloadPdf} className="secondary-btn">Download PDF</button></div>
          <div className="stops-grid">
            {trip.recommended_stops.length ? trip.recommended_stops.map(stop => (
              <article className="stop-card" key={stop.charger.id}>
                <strong>{stop.charger.name}</strong>
                <span>{stop.charger.city}</span>
                <div><b>{stop.charger.power_kw} kW</b><b>{stop.charger.available_probability}% available</b><b>{stop.charge_minutes} min</b></div>
                <small>{stop.reason}</small>
              </article>
            )) : <article className="stop-card"><strong>No stop required</strong><span>Current battery and buffer can complete this trip.</span></article>}
          </div>
          <div className="split-row">
            <BatteryGauge value={trip.arrival_battery_percent} label="arrival battery" />
            <div className="chart-box"><LineChart rows={trip.analytics.energy_series} /></div>
            <div className="cost-stack">
              <span>Charging cost <b>₹{trip.cost.charging_cost}</b></span>
              <span>Petrol savings <b>₹{trip.cost.petrol_savings}</b></span>
              <span>CO₂ saved <b>{trip.carbon.co2_saved_kg} kg</b></span>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
