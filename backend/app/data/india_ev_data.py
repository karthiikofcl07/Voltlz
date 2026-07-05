INDIAN_CITIES = {
    "Delhi, India": {"lat": 28.6139, "lng": 77.2090, "state": "Delhi"},
    "New Delhi, India": {"lat": 28.6139, "lng": 77.2090, "state": "Delhi"},
    "Manali, Himachal Pradesh": {"lat": 32.2396, "lng": 77.1887, "state": "Himachal Pradesh"},
    "Chandigarh, India": {"lat": 30.7333, "lng": 76.7794, "state": "Chandigarh"},
    "Mandi, Himachal Pradesh": {"lat": 31.7087, "lng": 76.9320, "state": "Himachal Pradesh"},
    "Ambala, Haryana": {"lat": 30.3782, "lng": 76.7767, "state": "Haryana"},
    "Bengaluru, Karnataka": {"lat": 12.9716, "lng": 77.5946, "state": "Karnataka"},
    "Mumbai, Maharashtra": {"lat": 19.0760, "lng": 72.8777, "state": "Maharashtra"},
    "Pune, Maharashtra": {"lat": 18.5204, "lng": 73.8567, "state": "Maharashtra"},
    "Hyderabad, Telangana": {"lat": 17.3850, "lng": 78.4867, "state": "Telangana"},
    "Chennai, Tamil Nadu": {"lat": 13.0827, "lng": 80.2707, "state": "Tamil Nadu"},
    "Ahmedabad, Gujarat": {"lat": 23.0225, "lng": 72.5714, "state": "Gujarat"},
    "Jaipur, Rajasthan": {"lat": 26.9124, "lng": 75.7873, "state": "Rajasthan"},
    "Agra, Uttar Pradesh": {"lat": 27.1767, "lng": 78.0081, "state": "Uttar Pradesh"},
    "Lucknow, Uttar Pradesh": {"lat": 26.8467, "lng": 80.9462, "state": "Uttar Pradesh"},
    "Kochi, Kerala": {"lat": 9.9312, "lng": 76.2673, "state": "Kerala"},
    "Goa, India": {"lat": 15.2993, "lng": 74.1240, "state": "Goa"},
    "Kolkata, West Bengal": {"lat": 22.5726, "lng": 88.3639, "state": "West Bengal"}
}

VEHICLES = {
    "Tata Nexon EV Max": {"capacity_kwh": 40.5, "usable_kwh": 38.1, "base_efficiency_wh_km": 132, "max_dc_kw": 50, "connector": "CCS2"},
    "Tata Tiago EV LR": {"capacity_kwh": 24.0, "usable_kwh": 22.5, "base_efficiency_wh_km": 118, "max_dc_kw": 25, "connector": "CCS2"},
    "MG ZS EV": {"capacity_kwh": 50.3, "usable_kwh": 47.7, "base_efficiency_wh_km": 147, "max_dc_kw": 76, "connector": "CCS2"},
    "Mahindra XUV400 EL": {"capacity_kwh": 39.4, "usable_kwh": 37.0, "base_efficiency_wh_km": 136, "max_dc_kw": 50, "connector": "CCS2"},
    "Hyundai Kona Electric": {"capacity_kwh": 39.2, "usable_kwh": 37.3, "base_efficiency_wh_km": 130, "max_dc_kw": 77, "connector": "CCS2"},
    "BYD Atto 3": {"capacity_kwh": 60.5, "usable_kwh": 57.5, "base_efficiency_wh_km": 150, "max_dc_kw": 88, "connector": "CCS2"}
}

CHARGERS = [
    {"id": "del-greencharge-cp", "name": "GreenCharge Station", "network": "GreenCharge", "city": "Connaught Place, Delhi", "lat": 28.6328, "lng": 77.2197, "power_kw": 150, "connectors": ["CCS2", "CHAdeMO", "Type 2"], "price_per_kwh": 18, "reliability": 0.94, "rating": 4.6, "availability": 0.92},
    {"id": "del-tatapower-saket", "name": "Tata Power EZ Charge", "network": "Tata Power", "city": "Saket, Delhi", "lat": 28.5245, "lng": 77.2066, "power_kw": 60, "connectors": ["CCS2", "Type 2"], "price_per_kwh": 20, "reliability": 0.91, "rating": 4.4, "availability": 0.85},
    {"id": "amb-statix-nh44", "name": "Statix Highway Hub", "network": "Statix", "city": "Ambala, Haryana", "lat": 30.3788, "lng": 76.7885, "power_kw": 120, "connectors": ["CCS2"], "price_per_kwh": 19, "reliability": 0.89, "rating": 4.3, "availability": 0.82},
    {"id": "chd-stateev-sector17", "name": "State EV Station", "network": "State EV", "city": "Sector 17, Chandigarh", "lat": 30.7415, "lng": 76.7821, "power_kw": 150, "connectors": ["CCS2", "Type 2"], "price_per_kwh": 17, "reliability": 0.95, "rating": 4.7, "availability": 0.92},
    {"id": "mandi-greencharge", "name": "GreenCharge Mandi", "network": "GreenCharge", "city": "Mandi, Himachal Pradesh", "lat": 31.7098, "lng": 76.9313, "power_kw": 120, "connectors": ["CCS2"], "price_per_kwh": 18, "reliability": 0.90, "rating": 4.5, "availability": 0.87},
    {"id": "manali-himalayan-ev", "name": "Himalayan EV Plaza", "network": "Himachal EV", "city": "Manali, Himachal Pradesh", "lat": 32.2360, "lng": 77.1860, "power_kw": 60, "connectors": ["CCS2", "Type 2"], "price_per_kwh": 21, "reliability": 0.86, "rating": 4.2, "availability": 0.74},
    {"id": "blr-indiranagar-ather", "name": "Ather Grid Indiranagar", "network": "Ather Grid", "city": "Indiranagar, Bengaluru", "lat": 12.9784, "lng": 77.6408, "power_kw": 50, "connectors": ["CCS2", "Type 2"], "price_per_kwh": 16, "reliability": 0.93, "rating": 4.5, "availability": 0.89},
    {"id": "blr-electroniccity-zeon", "name": "Zeon Charging Electronic City", "network": "Zeon", "city": "Electronic City, Bengaluru", "lat": 12.8399, "lng": 77.6770, "power_kw": 120, "connectors": ["CCS2"], "price_per_kwh": 19, "reliability": 0.92, "rating": 4.6, "availability": 0.88},
    {"id": "pune-tatapower-hinjewadi", "name": "Tata Power Hinjewadi", "network": "Tata Power", "city": "Hinjewadi, Pune", "lat": 18.5913, "lng": 73.7389, "power_kw": 60, "connectors": ["CCS2"], "price_per_kwh": 18, "reliability": 0.90, "rating": 4.4, "availability": 0.83},
    {"id": "mum-bkc-jio-bp", "name": "Jio-bp Pulse BKC", "network": "Jio-bp", "city": "Bandra Kurla Complex, Mumbai", "lat": 19.0667, "lng": 72.8675, "power_kw": 120, "connectors": ["CCS2", "Type 2"], "price_per_kwh": 20, "reliability": 0.91, "rating": 4.5, "availability": 0.78},
    {"id": "hyd-hitech-greenko", "name": "Greenko Charge Hub", "network": "Greenko", "city": "HITEC City, Hyderabad", "lat": 17.4435, "lng": 78.3772, "power_kw": 150, "connectors": ["CCS2"], "price_per_kwh": 17, "reliability": 0.94, "rating": 4.6, "availability": 0.86},
    {"id": "chn-omr-zeon", "name": "Zeon OMR Fast Charge", "network": "Zeon", "city": "OMR, Chennai", "lat": 12.9121, "lng": 80.2279, "power_kw": 120, "connectors": ["CCS2"], "price_per_kwh": 18, "reliability": 0.91, "rating": 4.4, "availability": 0.82},
    {"id": "jaipur-pulse-ajmerroad", "name": "Pulse Charge Ajmer Road", "network": "Pulse", "city": "Jaipur, Rajasthan", "lat": 26.8891, "lng": 75.7481, "power_kw": 90, "connectors": ["CCS2"], "price_per_kwh": 18, "reliability": 0.87, "rating": 4.3, "availability": 0.81},
    {"id": "agra-tatapower-yamuna", "name": "Tata Power Yamuna Express", "network": "Tata Power", "city": "Agra, Uttar Pradesh", "lat": 27.2020, "lng": 78.0382, "power_kw": 120, "connectors": ["CCS2"], "price_per_kwh": 19, "reliability": 0.89, "rating": 4.4, "availability": 0.84},
    {"id": "ahm-adani-sg", "name": "Adani TotalEnergies SG Highway", "network": "Adani TotalEnergies", "city": "Ahmedabad, Gujarat", "lat": 23.0720, "lng": 72.5166, "power_kw": 120, "connectors": ["CCS2", "Type 2"], "price_per_kwh": 18, "reliability": 0.92, "rating": 4.5, "availability": 0.85},
    {"id": "goa-zeon-panaji", "name": "Zeon Panaji Charge Point", "network": "Zeon", "city": "Panaji, Goa", "lat": 15.4909, "lng": 73.8278, "power_kw": 60, "connectors": ["CCS2"], "price_per_kwh": 20, "reliability": 0.88, "rating": 4.2, "availability": 0.76}
]
