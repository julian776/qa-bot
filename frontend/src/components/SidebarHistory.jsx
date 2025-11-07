export default function SidebarHistory({ conversations, onNew, onOpen, onDelete }) {
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
          <div key={c.id} className="conv" style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}>
            <div onClick={() => onOpen(c.id)} style={{cursor:'pointer',flex:1}}>
              <div className="title">{c.title}</div>
              <div className="date">{new Date(c.createdAt).toLocaleString()}</div>
            </div>
            <button
              className="btn warn"
              title="Eliminar chat"
              onClick={() => onDelete?.(c.id)}
              style={{marginLeft:8}}
            >
              🗑️
            </button>
          </div>
        ))}
      </div>
    </>
  );
}
