export function useLocalStore() {
  const conversations = JSON.parse(localStorage.getItem("chat.conversations") || "[]");
  const messagesByConv = JSON.parse(localStorage.getItem("chat.messages") || "{}");

  function setConversations(next) {
    localStorage.setItem("chat.conversations", JSON.stringify(next));
  }

  function setMessagesByConv(next) {
    localStorage.setItem("chat.messages", JSON.stringify(next));
  }

  function addConversation(conv) {
    const next = [{ id: conv.conversationId || conv.id, title: conv.title || "Nuevo chat", createdAt: Date.now() }, ...conversations];
    setConversations(next);
  }

  function setMessagesForConv(conversationId, msgs) {
    const next = { ...messagesByConv, [conversationId]: msgs };
    setMessagesByConv(next);
  }

  function appendMessage(conversationId, msg) {
    const next = { ...messagesByConv, [conversationId]: [ ...(messagesByConv[conversationId] || []), msg ] };
    setMessagesByConv(next);
  }

   // NUEVO: eliminar conversación + sus mensajes
  function deleteConversation(conversationId) {
    const nextConvs = conversations.filter(c => c.id !== conversationId);
    const { [conversationId]: _, ...restMsgs } = messagesByConv;
    setConversations(nextConvs);
    setMessagesByConv(restMsgs);
  }

  // Exponemos “estado” derivado desde localStorage;
  // App mantendrá su propio estado de UI.
  return {
    conversations: JSON.parse(localStorage.getItem("chat.conversations") || "[]"),
    messagesByConv: JSON.parse(localStorage.getItem("chat.messages") || "{}"),
    addConversation,
    setMessagesForConv,
    appendMessage,
    deleteConversation,
  };
}
