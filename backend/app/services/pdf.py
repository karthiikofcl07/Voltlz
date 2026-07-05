from __future__ import annotations

import textwrap


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_trip_pdf(trip: dict) -> bytes:
    lines = [
        "VoltNav 2.0 Intelligent EV Trip Report",
        f"Route: {trip['origin']} to {trip['destination']}",
        f"Vehicle: {trip['vehicle_model']}",
        f"Distance: {trip['distance_km']} km",
        f"Total Time: {trip['total_time']}",
        f"Charging Stops: {len(trip['recommended_stops'])}",
        f"Arrival Battery: {trip['arrival_battery_percent']}%",
        f"Estimated Charging Cost: INR {trip['cost']['charging_cost']}",
        f"Petrol Savings: INR {trip['cost']['petrol_savings']}",
        f"CO2 Saved: {trip['carbon']['co2_saved_kg']} kg",
        f"Risk Level: {trip['risk']['level']}",
        "",
        "Recommended Charging Stops:"
    ]
    if trip["recommended_stops"]:
        for stop in trip["recommended_stops"]:
            charger = stop["charger"]
            lines.append(f"- {charger['name']} ({charger['city']}): charge {stop['charge_minutes']} min, arrive {stop['arrival_soc']}%, leave {stop['departure_soc']}%, wait {stop['wait_minutes']} min")
    else:
        lines.append("- No charging stop required for this route and battery buffer.")
    lines.extend(["", "AI Explanation:", trip["assistant_summary"]])

    stream_lines = ["BT", "/F1 18 Tf", "54 780 Td", f"({_escape(lines[0])}) Tj", "/F1 10 Tf", "0 -28 Td"]
    for line in lines[1:]:
        wrapped = textwrap.wrap(str(line), width=92) or [""]
        for part in wrapped:
            stream_lines.append(f"({_escape(part)}) Tj")
            stream_lines.append("0 -15 Td")
    stream_lines.append("ET")
    content = "\n".join(stream_lines).encode("latin-1", "ignore")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n" + content + b"\nendstream"
    ]
    pdf = [b"%PDF-1.4\n"]
    offsets = [0]
    for i, obj in enumerate(objects, start=1):
        offsets.append(sum(len(x) for x in pdf))
        pdf.append(f"{i} 0 obj\n".encode() + obj + b"\nendobj\n")
    xref_offset = sum(len(x) for x in pdf)
    pdf.append(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        pdf.append(f"{offset:010d} 00000 n \n".encode())
    pdf.append(f"trailer << /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF".encode())
    return b"".join(pdf)
