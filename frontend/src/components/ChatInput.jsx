import { useState } from "react";

export default function ChatInput({ onSend, files, setFiles, disabled = false }) {
  const [text, setText] = useState("");

  function onPickFiles(e) {
    const list = Array.from(e.target.files || []);
    setFiles((prev) => [...prev, ...list]);
    e.target.value = "";
  }

  function removeFile(name) {
    setFiles((prev) => prev.filter((f) => f.name !== name));
  }

  function send() {
    if (disabled) return;
    onSend(text);
    if (text.trim()) setText("");
  }

  return (
    <>
      <div className="row" style={{ gridColumn: "1 / span 2" }}>
        <label htmlFor="file" className="btn ghost" aria-label="Adjuntar archivos">📎 Adjuntar</label>
        <input id="file" type="file" multiple style={{ display: "none" }} onChange={onPickFiles} />
        <div className="attachments">
          {files.map((f) => (
            <span key={f.name} className="chip" title={`${f.name} (${Math.round(f.size/1024)} KB)`}>
              {f.name}
              <span className="x" onClick={() => removeFile(f.name)} aria-label={`Quitar ${f.name}`}>×</span>
            </span>
          ))}
        </div>
      </div>

      <textarea
        aria-label="Escribe tu mensaje"
        placeholder={disabled ? "Procesando..." : "Escribe un mensaje… (Enter para enviar, Shift+Enter para salto de línea)"}
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey){ e.preventDefault(); send(); } }}
        rows={2}
        disabled={disabled}
      />
      <button className="btn primary" onClick={send} aria-label="Enviar" disabled={disabled}>Enviar</button>
    </>
  );
}
