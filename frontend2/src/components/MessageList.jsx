import { useEffect } from "react";
import MessageBubble from "./MessageBubble.jsx";

export default function MessageList({ messages, sending }) {
  useEffect(() => {
    function onClick(e) {
      const btn = e.target.closest(".copy-btn");
      if (!btn) return;
      const code = btn.getAttribute("data-code") || "";
      navigator.clipboard.writeText(code);
      btn.textContent = "Copiado";
      setTimeout(() => (btn.textContent = "Copiar"), 1200);
    }
    document.addEventListener("click", onClick);
    return () => document.removeEventListener("click", onClick);
  }, []);

  if (messages.length === 0)
    return (
      <div className="empty">
        <h2>¡Hola! 👋</h2>
        <p>Sube archivos y haz tu primera pregunta para comenzar.</p>
      </div>
    );

  return (
    <>
      {messages.map((m) => (
        <MessageBubble key={m.id} msg={m} />
      ))}
      {sending && (
        <div className="typing" aria-label="Escribiendo">
          <span className="dot" /><span className="dot" /><span className="dot" />
        </div>
      )}
    </>
  );
}
