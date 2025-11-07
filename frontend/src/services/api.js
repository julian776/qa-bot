export const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";
export const USE_MOCK = false; // Connected to real backend

export const api = {
  async send({ conversationId, message, files }) {
    if (USE_MOCK) return mockSendMessage({ conversationId, message, files });

    // Send query to backend first to ensure session exists
    const sessionId = conversationId || crypto.randomUUID();

    // If there are files, upload them with session_id
    if (files && files.length > 0) {
      for (const f of files) {
        const form = new FormData();
        form.append("file", f);
        form.append("user_id", "default_user");
        form.append("session_id", sessionId);

        const uploadRes = await fetch(`${API_BASE}/api/upload`, {
          method: "POST",
          body: form
        });
        if (!uploadRes.ok) throw new Error(`Upload failed: HTTP ${uploadRes.status}`);
      }
    }

    const res = await fetch(`${API_BASE}/api/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt: message,
        session_id: sessionId,
        user_id: "default_user",
        top_k: 10
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
      title: s.title || `Session ${s.session_id.substring(0, 8)}`,
      updated: s.updated_at,
      documentIds: s.document_ids || [],
      messageCount: s.message_count
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

  async uploadFiles(files, sessionId = null) {
    if (USE_MOCK) {
      await new Promise((r) => setTimeout(r, 400));
      return files.map((f) => ({ name: f.name, size: f.size }));
    }
    const results = [];
    for (const file of files) {
      const form = new FormData();
      form.append("file", file);
      form.append("user_id", "default_user");
      if (sessionId) {
        form.append("session_id", sessionId);
      }
      const res = await fetch(`${API_BASE}/api/upload`, { method: "POST", body: form });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      results.push({ name: file.name, size: file.size, uploaded: true });
    }
    return results;
  },

  async deleteConversation(conversationId) {
    if (USE_MOCK) return { success: true };
    const res = await fetch(`${API_BASE}/api/session/${conversationId}`, {
      method: "DELETE"
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  },

  async renameConversation(conversationId, newTitle) {
    if (USE_MOCK) return { success: true, title: newTitle };
    const res = await fetch(`${API_BASE}/api/session/${conversationId}/title`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: newTitle })
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  },

  async getSessionDocuments(conversationId) {
    if (USE_MOCK) return { documents: [], total_documents: 0 };
    const res = await fetch(`${API_BASE}/api/session/${conversationId}/documents`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  },

  async listDocuments() {
    if (USE_MOCK) return { documents: [], total_documents: 0 };
    const res = await fetch(`${API_BASE}/api/documents/default_user`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  },

  async deleteDocument(documentId) {
    if (USE_MOCK) return { success: true };
    const res = await fetch(`${API_BASE}/api/document/${documentId}`, {
      method: "DELETE"
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
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
