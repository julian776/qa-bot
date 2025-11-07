import { useState } from 'react';

export default function SidebarHistory({ conversations, onNew, onOpen, onDelete, onRename }) {
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState('');

  const handleStartEdit = (c) => {
    setEditingId(c.id);
    setEditTitle(c.title);
  };

  const handleSaveEdit = async (id) => {
    if (editTitle.trim() && editTitle !== conversations.find(c => c.id === id)?.title) {
      await onRename?.(id, editTitle.trim());
    }
    setEditingId(null);
    setEditTitle('');
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditTitle('');
  };

  return (
    <>
      <div className="head">
        <strong>Historial</strong>
        <button className="btn ghost" onClick={onNew}>+ Nuevo</button>
      </div>
      <div className="list">
        {conversations.length === 0 && (
          <div className="conv" style={{ opacity: 0.7 }}>Sin conversaciones</div>
        )}
        {conversations.map((c) => (
          <div key={c.id} className="conv" style={{display:'flex',justifyContent:'space-between',alignItems:'center',gap:4}}>
            <div onClick={() => onOpen(c.id)} style={{cursor:'pointer',flex:1,minWidth:0}}>
              {editingId === c.id ? (
                <input
                  type="text"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  onBlur={() => handleSaveEdit(c.id)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleSaveEdit(c.id);
                    if (e.key === 'Escape') handleCancelEdit();
                  }}
                  onClick={(e) => e.stopPropagation()}
                  autoFocus
                  style={{width:'100%',padding:'4px',fontSize:'14px'}}
                />
              ) : (
                <div className="title" onDoubleClick={(e) => { e.stopPropagation(); handleStartEdit(c); }}>
                  {c.title}
                  {c.documentIds && c.documentIds.length > 0 && (
                    <span style={{marginLeft:6,fontSize:11,opacity:0.7}} title={`${c.documentIds.length} documento(s)`}>
                      📎 {c.documentIds.length}
                    </span>
                  )}
                </div>
              )}
              <div className="date">{new Date(c.createdAt).toLocaleString()}</div>
            </div>
            <div style={{display:'flex',gap:4}}>
              <button
                className="btn ghost"
                title="Renombrar"
                onClick={(e) => { e.stopPropagation(); handleStartEdit(c); }}
                style={{padding:'4px 8px',fontSize:12}}
              >
                ✏️
              </button>
              <button
                className="btn warn"
                title="Eliminar chat"
                onClick={(e) => { e.stopPropagation(); onDelete?.(c.id); }}
                style={{padding:'4px 8px',fontSize:12}}
              >
                🗑️
              </button>
            </div>
          </div>
        ))}
      </div>
    </>
  );
}
