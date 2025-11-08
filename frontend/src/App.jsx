// src/App.jsx
import { useEffect, useMemo, useRef, useState } from "react";
import SidebarHistory from "./components/SidebarHistory.jsx";
import MessageList from "./components/MessageList.jsx";
import ChatInput from "./components/ChatInput.jsx";
import ThemeToggle from "./components/ThemeToggle.jsx";
import DocumentManager from "./components/DocumentManager.jsx";
import UserProfile from "./components/UserProfile.jsx";
import AuthPage from "./pages/AuthPage.jsx";
import { api } from "./services/api.js";
import { useLocalStore } from "./hooks/useLocalStore.js";
import { useAuth } from "./contexts/AuthContext.jsx";


export default function App() {
  const { user, loading: authLoading } = useAuth();
  const [conversationId, setConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [sending, setSending] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [files, setFiles] = useState([]);
  const [showDocuments, setShowDocuments] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const bottomRef = useRef(null);

  console.log('App render - authLoading:', authLoading, 'user:', user);

  // Show auth page if not logged in
  if (authLoading) {
    console.log('App: Showing loading screen');
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <div>Cargando...</div>
      </div>
    );
  }

  if (!user) {
    console.log('App: No user, showing auth page');
    return <AuthPage />;
  }

  console.log('App: User authenticated, showing main app');

  const { conversations, addConversation, messagesByConv, setMessagesForConv, appendMessage, deleteConversation } =
    useLocalStore();

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending]);

  useEffect(() => {
    // precarga (no es estrictamente necesario con mocks)
    api.listConversations().catch(() => {});
  }, []);

  const canSend = useMemo(() => !sending && !uploading, [sending, uploading]);

  async function ensureConversation() {
    if (conversationId) return conversationId;
    const { conversationId: id } = await api.newConversation();
    setConversationId(id);
    addConversation({ conversationId: id, title: "Nuevo chat" });
    setMessagesForConv(id, []);
    return id;
  }

  async function handleSend(text) {
    if (!text.trim() || !canSend || uploading) return;
    setError(null);
    const id = await ensureConversation();

    const userMsg = { id: crypto.randomUUID(), role: "user", content: text.trim(), createdAt: Date.now() };
    setMessages((prev) => [...prev, userMsg]);
    appendMessage(id, userMsg);

    // Upload files first if any
    if (files.length > 0) {
      setUploading(true);
      try {
        await api.uploadFiles(files, id);
        const uploadMsg = {
          id: crypto.randomUUID(),
          role: "system",
          content: `✅ ${files.length} documento${files.length > 1 ? 's' : ''} procesado${files.length > 1 ? 's' : ''} correctamente`,
          createdAt: Date.now()
        };
        setMessages((prev) => [...prev, uploadMsg]);
      } catch (e) {
        console.error("upload failed", e);
        setError(`Error al subir archivos: ${e.message}`);
        setUploading(false);
        return;
      } finally {
        setUploading(false);
      }
    }

    setSending(true);
    try {
      const data = await api.send({ conversationId: id, message: userMsg.content, files: [] });
      const botMsg = { id: crypto.randomUUID(), role: "assistant", content: data.reply, createdAt: Date.now() };
      setMessages((prev) => [...prev, botMsg]);
      appendMessage(id, botMsg);
      setFiles([]);
    } catch (e) {
      console.error(e);
      setError("No se pudo enviar. Reintenta.");
    } finally {
      setSending(false);
    }
  }

  async function handleNewChat() {
    const { conversationId: id } = await api.newConversation();
    setConversationId(id);
    addConversation({ conversationId: id, title: "Nuevo chat" });
    setMessages([]);
    setMessagesForConv(id, []);
    setFiles([]);
    setError(null);
  }

  async function openConversation(id) {
    setConversationId(id);
    try {
      const msgs = await api.getMessages(id);
      setMessages(msgs);
      setError(null);
    } catch {
      setMessages(messagesByConv[id] || []);
    }
  }

  async function handleDeleteConversation(id) {
    if (!confirm("¿Eliminar este chat? Esta acción no se puede deshacer.")) return;

    try {
      // Delete from backend
      await api.deleteConversation(id);

      // Delete from local state
      deleteConversation(id);

      // If deleting the active chat, clear the view
      if (id === conversationId) {
        setConversationId(null);
        setMessages([]);
      }
    } catch (e) {
      console.error("Error deleting conversation:", e);
      setError(`Error al eliminar el chat: ${e.message}`);
    }
  }

  async function handleRenameConversation(id, newTitle) {
    try {
      // Update in backend
      await api.renameConversation(id, newTitle);

      // Update in local state
      const updatedConvs = conversations.map(c =>
        c.id === id ? { ...c, title: newTitle } : c
      );
      // We need to update localStorage here
      localStorage.setItem("chat.conversations", JSON.stringify(updatedConvs));
      window.location.reload(); // Simple refresh to sync state
    } catch (e) {
      console.error("Error renaming conversation:", e);
      setError(`Error al renombrar el chat: ${e.message}`);
    }
  }


  return (
    <div className="app">
      <aside className="sidebar" aria-label="Historial de conversaciones">
        <SidebarHistory
          conversations={conversations}
          onNew={handleNewChat}
          onOpen={openConversation}
          onDelete={handleDeleteConversation}
          onRename={handleRenameConversation}
        />
      </aside>

      <section className="main">
        <div className="topbar">
          <div className="brand">
            <div className="logo">🤖</div>
            <div>Interfaz de Chat</div>
          </div>
          <div className="actions">
            <button
              className="btn ghost"
              onClick={() => setShowDocuments(!showDocuments)}
              title="Ver documentos de la sesión"
            >
              📎 Documentos
            </button>
            <button
              className="btn ghost"
              onClick={() => setShowProfile(true)}
              title="Mi perfil"
            >
              👤 {user?.username}
            </button>
            <ThemeToggle />
          </div>
        </div>

        <div className="messages" role="log" aria-live="polite">
          <MessageList messages={messages} sending={sending} uploading={uploading} />
          <div ref={bottomRef} />
        </div>

        <div className="input">
          {error && <span className="error">{error}</span>}
          <ChatInput
            onSend={handleSend}
            files={files}
            setFiles={setFiles}
            disabled={!canSend}
          />
        </div>
      </section>

      {showDocuments && (
        <aside className="sidebar" style={{ borderLeft: '1px solid var(--border)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: 16, borderBottom: '1px solid var(--border)' }}>
            <strong>Documentos</strong>
            <button
              className="btn ghost"
              onClick={() => setShowDocuments(false)}
              style={{ padding: '4px 8px' }}
            >
              ✕
            </button>
          </div>
          <DocumentManager conversationId={conversationId} />
        </aside>
      )}

      {showProfile && (
        <UserProfile onClose={() => setShowProfile(false)} />
      )}
    </div>
  );
}
