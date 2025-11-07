const URL_REGEX = /((https?:\/\/)[^\s)]+)|(^www\.[^\s)]+)/gi;

export function basicMarkdownToHtml(md) {
  if (!md) return "";
  let h = md.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

  // ```code```
  h = h.replace(/```([\s\S]*?)```/g, (m, code) => {
    const esc = code.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    return `<pre class="code-block"><code>${esc}</code><button class="copy-btn" data-code="${esc.replace(/"/g, "&quot;")}">Copiar</button></pre>`;
  });

  h = h.replace(/^###\s+(.*)$/gim, "<h3>$1</h3>");
  h = h.replace(/^##\s+(.*)$/gim, "<h2>$1</h2>");
  h = h.replace(/^#\s+(.*)$/gim, "<h1>$1</h1>");

  h = h.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  h = h.replace(/\*(.*?)\*/g, "<em>$1</em>");
  h = h.replace(/`([^`]+)`/g, '<code class="code-inline">$1</code>');

  h = h.replace(/^(?:-|\*)\s+(.+)$/gim, "<li>$1</li>");
  h = h.replace(/(<li>.*<\/li>)/gims, "<ul>$1</ul>");

  h = h.replace(/\n/g, "<br />");
  return h;
}

export function extractLinks(text) {
  const links = [];
  if (!text) return links;
  const m = text.match(URL_REGEX) || [];
  for (const u of m) {
    const url = u.startsWith("http") ? u : `https://${u}`;
    try {
      const { hostname } = new URL(url);
      links.push({ url, host: hostname });
    } catch {}
  }
  return links.filter((x, i, a) => a.findIndex(y => y.url === x.url) === i);
}
