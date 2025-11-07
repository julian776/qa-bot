import { useState, useEffect } from 'react';
import { api } from '../services/api.js';

export default function DocumentManager({ conversationId }) {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (conversationId) {
      loadDocuments();
    }
  }, [conversationId]);

  async function loadDocuments() {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getSessionDocuments(conversationId);
      setDocuments(data.documents || []);
    } catch (e) {
      console.error("Error loading documents:", e);
      setError(`Error al cargar documentos: ${e.message}`);
    } finally {
      setLoading(false);
    }
  }

  async function handleDeleteDocument(documentId) {
    if (!confirm("¿Eliminar este documento? Se eliminará de todas las sesiones.")) return;

    try {
      await api.deleteDocument(documentId);
      setDocuments(docs => docs.filter(d => d.id !== documentId));
    } catch (e) {
      console.error("Error deleting document:", e);
      setError(`Error al eliminar documento: ${e.message}`);
    }
  }

  if (!conversationId) {
    return (
      <div style={{ padding: 16, textAlign: 'center', opacity: 0.7 }}>
        Selecciona o crea una conversación para ver documentos
      </div>
    );
  }

  if (loading) {
    return <div style={{ padding: 16, textAlign: 'center' }}>Cargando documentos...</div>;
  }

  return (
    <div style={{ padding: 16 }}>
      <h3 style={{ marginTop: 0 }}>Documentos en esta sesión</h3>
      {error && <div style={{ color: 'var(--error)', marginBottom: 8 }}>{error}</div>}

      {documents.length === 0 ? (
        <div style={{ opacity: 0.7, fontSize: 14 }}>
          No hay documentos vinculados a esta sesión.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {documents.map(doc => (
            <div
              key={doc.id}
              style={{
                padding: 12,
                border: '1px solid var(--border)',
                borderRadius: 6,
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}
            >
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontWeight: 500, marginBottom: 4 }}>
                  📄 {doc.original_filename || doc.filename}
                </div>
                <div style={{ fontSize: 12, opacity: 0.7 }}>
                  {doc.total_chunks} chunks • {doc.file_type} • {(doc.file_size / 1024).toFixed(1)} KB
                </div>
                <div style={{ fontSize: 11, opacity: 0.6, marginTop: 2 }}>
                  Subido: {new Date(doc.created_at).toLocaleString()}
                </div>
              </div>
              <button
                className="btn warn"
                onClick={() => handleDeleteDocument(doc.id)}
                style={{ padding: '6px 12px', fontSize: 12 }}
                title="Eliminar documento"
              >
                🗑️
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
