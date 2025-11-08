import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

export default function UserProfile({ onClose }) {
  const { user, logout, updateProfile } = useAuth();
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({
    username: user?.username || '',
    fullName: user?.full_name || '',
    email: user?.email || ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  function handleChange(e) {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  }

  async function handleSave() {
    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const updates = {};
      if (formData.username !== user.username) updates.username = formData.username;
      if (formData.fullName !== (user.full_name || '')) updates.full_name = formData.fullName;
      if (formData.email !== user.email) updates.email = formData.email;

      if (Object.keys(updates).length === 0) {
        setMessage({ type: 'info', text: 'No hay cambios para guardar' });
        setEditing(false);
        return;
      }

      const result = await updateProfile(updates);

      if (result.success) {
        setMessage({ type: 'success', text: '✓ Perfil actualizado correctamente' });
        setEditing(false);
      } else {
        setMessage({ type: 'error', text: result.error });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Error al actualizar el perfil' });
    } finally {
      setLoading(false);
    }
  }

  function handleCancel() {
    setFormData({
      username: user?.username || '',
      fullName: user?.full_name || '',
      email: user?.email || ''
    });
    setEditing(false);
    setMessage({ type: '', text: '' });
  }

  return (
    <div style={styles.overlay} onClick={onClose}>
      <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div style={styles.header}>
          <h2 style={styles.title}>Mi Perfil</h2>
          <button onClick={onClose} style={styles.closeBtn}>✕</button>
        </div>

        <div style={styles.content}>
          {message.text && (
            <div style={{
              ...styles.message,
              background: message.type === 'error' ? '#fee' : message.type === 'success' ? '#efe' : '#eef',
              color: message.type === 'error' ? '#c33' : message.type === 'success' ? '#3c3' : '#33c'
            }}>
              {message.text}
            </div>
          )}

          <div style={styles.field}>
            <label style={styles.label}>Correo Electrónico</label>
            {editing ? (
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                style={styles.input}
                disabled={loading}
              />
            ) : (
              <div style={styles.value}>{user?.email}</div>
            )}
          </div>

          <div style={styles.field}>
            <label style={styles.label}>Nombre de Usuario</label>
            {editing ? (
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                style={styles.input}
                disabled={loading}
              />
            ) : (
              <div style={styles.value}>{user?.username}</div>
            )}
          </div>

          <div style={styles.field}>
            <label style={styles.label}>Nombre Completo</label>
            {editing ? (
              <input
                type="text"
                name="fullName"
                value={formData.fullName}
                onChange={handleChange}
                style={styles.input}
                placeholder="Tu nombre completo"
                disabled={loading}
              />
            ) : (
              <div style={styles.value}>{user?.full_name || '(No especificado)'}</div>
            )}
          </div>

          <div style={styles.field}>
            <label style={styles.label}>Miembro desde</label>
            <div style={styles.value}>
              {user?.created_at ? new Date(user.created_at).toLocaleDateString() : '-'}
            </div>
          </div>

          <div style={styles.field}>
            <label style={styles.label}>Último acceso</label>
            <div style={styles.value}>
              {user?.last_login ? new Date(user.last_login).toLocaleString() : '-'}
            </div>
          </div>
        </div>

        <div style={styles.footer}>
          {editing ? (
            <>
              <button
                className="btn ghost"
                onClick={handleCancel}
                disabled={loading}
                style={{ marginRight: '8px' }}
              >
                Cancelar
              </button>
              <button
                className="btn primary"
                onClick={handleSave}
                disabled={loading}
              >
                {loading ? 'Guardando...' : 'Guardar Cambios'}
              </button>
            </>
          ) : (
            <>
              <button
                className="btn ghost"
                onClick={logout}
                style={{ marginRight: 'auto' }}
              >
                Cerrar Sesión
              </button>
              <button
                className="btn primary"
                onClick={() => setEditing(true)}
              >
                Editar Perfil
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

const styles = {
  overlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'rgba(0,0,0,0.5)',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000
  },
  modal: {
    background: 'var(--bg)',
    borderRadius: '12px',
    width: '90%',
    maxWidth: '500px',
    maxHeight: '90vh',
    overflow: 'auto',
    boxShadow: '0 20px 60px rgba(0,0,0,0.3)'
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '20px 24px',
    borderBottom: '1px solid var(--border)'
  },
  title: {
    margin: 0,
    fontSize: '20px',
    fontWeight: '600'
  },
  closeBtn: {
    background: 'none',
    border: 'none',
    fontSize: '24px',
    cursor: 'pointer',
    padding: '4px 8px',
    lineHeight: 1,
    color: 'var(--text)'
  },
  content: {
    padding: '24px',
    display: 'flex',
    flexDirection: 'column',
    gap: '20px'
  },
  message: {
    padding: '12px',
    borderRadius: '6px',
    fontSize: '14px'
  },
  field: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px'
  },
  label: {
    fontSize: '13px',
    fontWeight: '500',
    color: 'var(--text-secondary)',
    textTransform: 'uppercase',
    letterSpacing: '0.5px'
  },
  value: {
    fontSize: '15px',
    color: 'var(--text)'
  },
  input: {
    padding: '10px 12px',
    border: '1px solid var(--border)',
    borderRadius: '6px',
    fontSize: '15px',
    background: 'var(--bg)',
    color: 'var(--text)'
  },
  footer: {
    display: 'flex',
    justifyContent: 'flex-end',
    padding: '16px 24px',
    borderTop: '1px solid var(--border)',
    gap: '8px'
  }
};
