export function Brand({ compact = false }) {
  return (
    <div className="brand">
      <img src="/voltnav-mark.svg" alt="" />
      <div>
        <strong>VoltNav</strong>
        {!compact && <span>Smart EV Trip Planner</span>}
      </div>
      {!compact && <small>2.0</small>}
    </div>
  );
}
