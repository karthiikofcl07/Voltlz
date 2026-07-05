import { useEffect, useRef } from 'react';
import L from 'leaflet';

function icon(cls, label) {
  return L.divIcon({
    className: `volt-marker ${cls}`,
    html: `<span>${label || ''}</span>`,
    iconSize: [30, 30],
    iconAnchor: [15, 15]
  });
}

export function MapPanel({ trip, chargers = [], focus = [28.6139, 77.2090], className = '' }) {
  const divRef = useRef(null);
  const mapRef = useRef(null);
  useEffect(() => {
    if (!divRef.current) return;
    if (!mapRef.current) {
      mapRef.current = L.map(divRef.current, { zoomControl: false, attributionControl: true });
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors'
      }).addTo(mapRef.current);
      L.control.zoom({ position: 'bottomright' }).addTo(mapRef.current);
    }
    const map = mapRef.current;
    map.eachLayer(layer => {
      if (!layer._url) map.removeLayer(layer);
    });
    const bounds = [];
    if (trip?.route?.length) {
      const line = trip.route.map(p => [p.lat, p.lng]);
      L.polyline(line, { color: '#4cc9ff', weight: 5, opacity: 0.88 }).addTo(map);
      L.polyline(line, { color: '#36f69a', weight: 1.5, opacity: 0.9 }).addTo(map);
      const first = line[0];
      const last = line[line.length - 1];
      L.marker(first, { icon: icon('start', 'S') }).bindPopup(trip.origin).addTo(map);
      L.marker(last, { icon: icon('dest', 'D') }).bindPopup(trip.destination).addTo(map);
      bounds.push(...line);
      trip.recommended_stops?.forEach((stop, idx) => {
        const c = stop.charger;
        L.marker([c.lat, c.lng], { icon: icon('stop', String(idx + 1)) })
          .bindPopup(`<b>${c.name}</b><br>${c.power_kw} kW ${c.network}<br>${c.available_probability}% available`)
          .addTo(map);
        bounds.push([c.lat, c.lng]);
      });
    } else {
      chargers.forEach((c, idx) => {
        L.marker([c.lat, c.lng], { icon: icon('charger', String(idx + 1)) })
          .bindPopup(`<b>${c.name}</b><br>${c.city}<br>${c.power_kw} kW`)
          .addTo(map);
        bounds.push([c.lat, c.lng]);
      });
    }
    if (bounds.length) map.fitBounds(bounds, { padding: [42, 42], maxZoom: 9 });
    else map.setView(focus, 10);
    setTimeout(() => map.invalidateSize(), 120);
  }, [trip, chargers, focus]);
  return <div ref={divRef} className={`map-panel ${className}`} />;
}
