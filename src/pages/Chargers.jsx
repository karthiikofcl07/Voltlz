import { useEffect, useState } from 'react';
import { VoltApi } from '../api.js';
import { MapPanel } from '../components/MapPanel.jsx';

export default function Chargers() {
  const [query, setQuery] = useState('');
  const [chargers, setChargers] = useState([]);
  const [selected, setSelected] = useState(null);
  useEffect(() => {
    VoltApi.chargers(query).then(data => {
      setChargers(data.chargers);
      setSelected(prev => prev || data.chargers[0]);
    });
  }, [query]);
  return (
    <div className="chargers-layout">
      <section className="panel charger-list">
        <div className="panel-head"><div><p className="eyebrow">Unified discovery</p><h2>Charging stations</h2></div></div>
        <input className="search" placeholder="Search station, city or network" value={query} onChange={e => setQuery(e.target.value)} />
        <div className="station-list">
          {chargers.map((c, idx) => (
            <button key={c.id} className={selected?.id === c.id ? 'station active' : 'station'} onClick={() => setSelected(c)}>
              <b>{idx + 1}</b>
              <span><strong>{c.name}</strong><small>{c.city}</small><small>{c.power_kw} kW DC Fast · Available {c.available_probability}%</small></span>
              <em>{c.price_per_kwh}/kWh</em>
            </button>
          ))}
        </div>
      </section>
      <section className="panel charger-map">
        <MapPanel chargers={chargers} />
      </section>
      <aside className="panel station-detail">
        {selected && (
          <>
            <p className="eyebrow">{selected.network}</p>
            <h2>{selected.name}</h2>
            <p>{selected.city}</p>
            <div className="detail-grid">
              <span>Power <b>{selected.power_kw} kW</b></span>
              <span>Reliability <b>{Math.round(selected.reliability * 100)}%</b></span>
              <span>Available <b>{selected.available_probability}%</b></span>
              <span>Wait <b>{selected.wait_minutes} min</b></span>
              <span>Rating <b>{selected.rating}/5</b></span>
              <span>Price <b>₹{selected.price_per_kwh}/kWh</b></span>
            </div>
            <h3>AI review summary</h3>
            <p className="assistant-note">Drivers report stable charging speed and clear bay access. Evening availability can reduce near city centers, so VoltNav adds predicted wait time before selecting this charger.</p>
            <button className="primary-btn">View details</button>
          </>
        )}
      </aside>
    </div>
  );
}
