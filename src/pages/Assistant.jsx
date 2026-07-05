import { useEffect, useRef, useState } from 'react';
import { VoltApi } from '../api.js';

export default function Assistant() {
  const [messages, setMessages] = useState([{ role: 'ai', text: 'Hi, I am VoltNav AI. Ask why a charger was selected, whether you can skip a stop, or how much money you save.' }]);
  const [text, setText] = useState('Is it necessary to stop at Chandigarh?');
  const [busy, setBusy] = useState(false);
  const bottom = useRef(null);
  useEffect(() => { bottom.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  async function send(e) {
    e.preventDefault();
    if (!text.trim()) return;
    const userText = text.trim();
    setMessages(prev => [...prev, { role: 'user', text: userText }]);
    setText('');
    setBusy(true);
    try {
      const res = await VoltApi.assistant({ message: userText });
      setMessages(prev => [...prev, { role: 'ai', text: res.answer }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="assistant-layout">
      <section className="panel chat-panel">
        <div className="panel-head"><div><p className="eyebrow">AI charging assistant</p><h2>Explainable trip decisions</h2></div><button className="ghost tiny" onClick={() => setMessages([])}>New chat</button></div>
        <div className="chat-stream">
          {messages.map((m, i) => <div key={i} className={`message ${m.role}`}>{m.text}</div>)}
          {busy && <div className="message ai">Analyzing route plan...</div>}
          <div ref={bottom} />
        </div>
        <form className="chat-input" onSubmit={send}>
          <input value={text} onChange={e => setText(e.target.value)} placeholder="Ask anything about this trip" />
          <button className="primary-btn small">Send</button>
        </form>
      </section>
      <aside className="panel assistant-side">
        <h2>Suggested questions</h2>
        {['Why stop here?', 'Can I skip this charger?', 'Should I charge to 80% or 100%?', 'How much money will I save?'].map(q => <button key={q} onClick={() => setText(q)}>{q}</button>)}
      </aside>
    </div>
  );
}
