export const API_BASE = import.meta.env.VITE_API_BASE || "";
export const USE_MOCK = true; // ← pon false cuando conectes tu backend

export const api = {
  async send({ conversationId, message, files }) {
    if (USE_MOCK) return mockSendMessage({ conversationId, message, files });
    const form = new FormData();
    form.append("message", message);
    if (conversationId) form.append("conversationId", conversationId);
    for (const f of files || []) form.append("files", f);
    const res = await fetch(`${API_BASE}/api/chat/send`, { method: "POST", body: form });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  },
  async listConversations() {
    if (USE_MOCK) return mockListConversations();
    const res = await fetch(`${API_BASE}/api/conversations`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  },
  async getMessages(conversationId) {
    if (USE_MOCK) return mockListMessages(conversationId);
    const res = await fetch(`${API_BASE}/api/conversations/${conversationId}/messages`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  },
  async newConversation() {
    if (USE_MOCK) return { conversationId: crypto.randomUUID(), title: "Nuevo chat" };
    const res = await fetch(`${API_BASE}/api/conversations`, { method: "POST" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  },
  async uploadFiles(files) {
    if (USE_MOCK) {
      await new Promise((r) => setTimeout(r, 400));
      return files.map((f) => ({ name: f.name, size: f.size }));
    }
    const form = new FormData();
    for (const f of files) form.append("files", f);
    const res = await fetch(`${API_BASE}/api/files/upload`, { method: "POST", body: form });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  },
};

// ====== MOCKS ======
async function mockSendMessage({ conversationId, message, files }) {
  await new Promise((r) => setTimeout(r, 700));
  const reply = `# Respuesta de ejemplo\n\n**Recibí:** ${message}\n\n- Puedo manejar *listas* y \`código\`\n- Archivos adjuntos: ${files?.length || 0}\n\n\`\`\`js\nconsole.log('Hola desde el mock');\n\`\`\``;
  return { reply, conversationId: conversationId || crypto.randomUUID() };
}
async function mockListConversations() {
  await new Promise((r) => setTimeout(r, 120));
  const raw = JSON.parse(localStorage.getItem("chat.conversations") || "[]");
  return raw;
}
async function mockListMessages(conversationId) {
  await new Promise((r) => setTimeout(r, 120));
  const all = JSON.parse(localStorage.getItem("chat.messages") || "{}");
  return all[conversationId] || [];
}
