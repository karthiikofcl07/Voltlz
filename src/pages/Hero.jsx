import { Link } from 'react-router-dom';
import { Brand } from '../components/Brand.jsx';
import { MapPanel } from '../components/MapPanel.jsx';

export default function Hero() {
  const demoTrip = {
    origin: 'Delhi, India',
    destination: 'Manali, Himachal Pradesh',
    route: [
      { lat: 28.6139, lng: 77.2090 }, { lat: 30.7333, lng: 76.7794 }, { lat: 31.7087, lng: 76.9320 }, { lat: 32.2396, lng: 77.1887 }
    ],
    recommended_stops: [
      { charger: { name: 'State EV Station', lat: 30.7415, lng: 76.7821, power_kw: 150, network: 'State EV', available_probability: 92 } },
      { charger: { name: 'GreenCharge Mandi', lat: 31.7098, lng: 76.9313, power_kw: 120, network: 'GreenCharge', available_probability: 87 } }
    ]
  };
  return (
    <div className="hero-page">
      <header className="hero-nav">
        <Brand />
        <Link to="/login" className="primary-btn small">Launch App</Link>
      </header>
      <section className="hero-grid">
        <div className="hero-copy">
          <p className="eyebrow">AI-powered EV travel assistant for India</p>
          <h1>Plan longer EV journeys with fewer charging surprises.</h1>
          <p className="hero-sub">
            VoltNav combines a physics-informed range model, machine learning, route energy analysis, charger reliability and price intelligence to recommend only the charging stops you need.
          </p>
          <div className="hero-actions">
            <Link to="/login" className="primary-btn">Get started</Link>
            <a href="#architecture" className="secondary-btn">See platform</a>
          </div>
          <div className="hero-metrics">
            <span><b>317 km</b> predicted range</span>
            <span><b>2</b> optimized stops</span>
            <span><b>46.8 kg</b> CO₂ saved</span>
          </div>
        </div>
        <div className="hero-phone">
          <div className="phone-screen">
            <div className="phone-status">VoltNav route intelligence</div>
            <MapPanel trip={demoTrip} />
            <div className="phone-card">
              <strong>Delhi to Manali</strong>
              <span>Safe route, 22% arrival battery</span>
            </div>
          </div>
        </div>
      </section>
      <section id="architecture" className="hero-band">
        {['Hybrid ML + Physics', 'OpenStreetMap + Charger Layer', 'PDF Itinerary', 'Trip History', 'Battery Health', 'AI Assistant'].map(item => <span key={item}>{item}</span>)}
      </section>
    </div>
  );
}
