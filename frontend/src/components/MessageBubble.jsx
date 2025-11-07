import { basicMarkdownToHtml, extractLinks } from "../services/markdown.js";

export default function MessageBubble({ msg }) {
  const isUser = msg.role === "user";
  const isSystem = msg.role === "system";
  const links = extractLinks(msg.content);
  const html = basicMarkdownToHtml(msg.content);

  if (isSystem) {
    return (
      <div className="bubble system" style={{ textAlign: "center", opacity: 0.8, fontStyle: "italic" }}>
        <div className="msg">
          <div dangerouslySetInnerHTML={{ __html: html }} />
        </div>
      </div>
    );
  }

  return (
    <div className={`bubble ${isUser ? "user" : "bot"}`}>
      {!isUser && <div className="avatar">🤖</div>}
      <div className="msg">
        <div dangerouslySetInnerHTML={{ __html: html }} />
        {!isUser && links.length > 0 && (
          <div className="links">
            {links.map((l) => (
              <span key={l.url} className="link-chip">
                🔗 <a href={l.url} target="_blank" rel="noreferrer">{l.host}</a>
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
