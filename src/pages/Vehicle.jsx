import { useEffect, useState } from 'react';
import { VoltApi } from '../api.js';
import { BatteryGauge, StatCard } from '../components/StatCard.jsx';

export default function Vehicle() {
  const [meta, setMeta] = useState({ vehicles: {} });
  const [form, setForm] = useState({ vehicle_model: 'Tata Nexon EV Max', odometer_km: 18400, vehicle_age_months: 18, fast_charge_ratio: 0.32, cycles: 512, hot_days: 110 });
  const [profile, setProfile] = useState(null);
  useEffect(() => { VoltApi.meta().then(setMeta); VoltApi.vehicle(form).then(setProfile); }, []);
  function update(name, value) {
    setForm(prev => ({ ...prev, [name]: name === 'vehicle_model' ? value : Number(value) }));
  }
  async function submit(e) {
    e.preventDefault();
    setProfile(await VoltApi.vehicle(form));
  }
  const vehicle = meta.vehicles[form.vehicle_model];
  return (
    <div className="vehicle-layout">
      <section className="panel">
        <div className="panel-head"><div><p className="eyebrow">Vehicle digital twin</p><h2>{form.vehicle_model}</h2></div></div>
        <BatteryGauge value={profile?.health?.state_of_health || 92} label="battery state of health" />
        <div className="stat-strip compact">
          <StatCard label="Usable pack" value={`${vehicle?.usable_kwh || 38.1} kWh`} sub="model profile" />
          <StatCard label="Max DC" value={`${vehicle?.max_dc_kw || 50} kW`} sub="charge curve cap" tone="cyan" />
          <StatCard label="Efficiency" value={`${vehicle ? (1000 / vehicle.base_efficiency_wh_km).toFixed(1) : 7.6} km/kWh`} sub="baseline" />
        </div>
        {profile && <p className="assistant-note">{profile.health.recommendation}. Estimated replacement planning horizon: {profile.health.replacement_timeline_years} years.</p>}
      </section>
      <form className="panel vehicle-form" onSubmit={submit}>
        <h2>Update battery profile</h2>
        <label>Vehicle<select value={form.vehicle_model} onChange={e => update('vehicle_model', e.target.value)}>{Object.keys(meta.vehicles).map(v => <option key={v}>{v}</option>)}</select></label>
        <label>Odometer km<input type="number" value={form.odometer_km} onChange={e => update('odometer_km', e.target.value)} /></label>
        <label>Vehicle age months<input type="number" value={form.vehicle_age_months} onChange={e => update('vehicle_age_months', e.target.value)} /></label>
        <label>Fast charge ratio<input type="number" step="0.01" min="0" max="1" value={form.fast_charge_ratio} onChange={e => update('fast_charge_ratio', e.target.value)} /></label>
        <label>Charge cycles<input type="number" value={form.cycles} onChange={e => update('cycles', e.target.value)} /></label>
        <button className="primary-btn">Recalculate health</button>
      </form>
      <section className="panel">
        <h2>Roadmap-ready intelligence</h2>
        <div className="timeline">
          {['Digital twin learns real efficiency from trip history', 'Battery degradation uses cycles, charging speed and hot-day exposure', 'Future LSTM model can be swapped behind the same API', 'Fleet mode can monitor multiple vehicles and charging costs'].map(x => <span key={x}>{x}</span>)}
        </div>
      </section>
    </div>
  );
}
