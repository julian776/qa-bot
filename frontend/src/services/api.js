export const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";
export const USE_MOCK = false; // Connected to real backend

export const api = {
  async send({ conversationId, message, files }) {
    if (USE_MOCK) return mockSendMessage({ conversationId, message, files });

    // If there are files, upload them first
    if (files && files.length > 0) {
      const form = new FormData();
      for (const f of files) form.append("file", f);
      form.append("user_id", "default_user");

      const uploadRes = await fetch(`${API_BASE}/api/upload`, {
        method: "POST",
        body: form
      });
      if (!uploadRes.ok) throw new Error(`Upload failed: HTTP ${uploadRes.status}`);
    }

    // Send query to backend
    const sessionId = conversationId || crypto.randomUUID();
    const res = await fetch(`${API_BASE}/api/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt: message,
        session_id: sessionId,
        user_id: "default_user",
        top_k: 5
      })
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return {
      reply: data.answer,
      conversationId: sessionId,
      language: data.language,
      sources: data.sources
    };
  },

  async listConversations() {
    if (USE_MOCK) return mockListConversations();
    const res = await fetch(`${API_BASE}/api/sessions/default_user`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return data.sessions.map(s => ({
      conversationId: s.session_id,
      title: `Session ${s.session_id.substring(0, 8)}`,
      updated: s.updated_at
    }));
  },

  async getMessages(conversationId) {
    if (USE_MOCK) return mockListMessages(conversationId);
    const res = await fetch(`${API_BASE}/api/session/${conversationId}/messages`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return data.messages.map(m => ({
      role: m.role,
      content: m.content,
      timestamp: m.created_at
    }));
  },

  async newConversation() {
    if (USE_MOCK) return { conversationId: crypto.randomUUID(), title: "Nuevo chat" };
    const res = await fetch(`${API_BASE}/api/session/create`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: "default_user" })
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return {
      conversationId: data.session_id,
      title: `New session ${data.session_id.substring(0, 8)}`
    };
  },

  async uploadFiles(files) {
    if (USE_MOCK) {
      await new Promise((r) => setTimeout(r, 400));
      return files.map((f) => ({ name: f.name, size: f.size }));
    }
    const results = [];
    for (const file of files) {
      const form = new FormData();
      form.append("file", file);
      form.append("user_id", "default_user");
      const res = await fetch(`${API_BASE}/api/upload`, { method: "POST", body: form });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      results.push({ name: file.name, size: file.size, uploaded: true });
    }
    return results;
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
