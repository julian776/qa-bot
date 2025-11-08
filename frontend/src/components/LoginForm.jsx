import { useState } from 'react';

export default function LoginForm({ onLogin, onSwitchToRegister, error: externalError }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      console.log('LoginForm: Calling onLogin...');
      const result = await onLogin(email, password);
      console.log('LoginForm: Login result:', result);

      if (!result.success) {
        console.log('LoginForm: Login failed:', result.error);
        setError(result.error);
        setLoading(false);
      } else {
        console.log('LoginForm: Login successful, should redirect now');
        // Keep loading state to prevent UI flash before redirect
      }
    } catch (err) {
      console.error('LoginForm: Exception during login:', err);
      setError('Login failed. Please try again.');
      setLoading(false);
    }
  }

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2 style={styles.title}>Iniciar Sesión</h2>
        <p style={styles.subtitle}>Accede a tu cuenta para continuar</p>

        <form onSubmit={handleSubmit} style={styles.form}>
          {(error || externalError) && (
            <div style={styles.error}>
              {error || externalError}
            </div>
          )}

          <div style={styles.inputGroup}>
            <label style={styles.label}>Correo Electrónico</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="tu@email.com"
              style={styles.input}
              disabled={loading}
            />
          </div>

          <div style={styles.inputGroup}>
            <label style={styles.label}>Contraseña</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="••••••••"
              style={styles.input}
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            className="btn primary"
            style={styles.button}
            disabled={loading}
          >
            {loading ? 'Iniciando...' : 'Iniciar Sesión'}
          </button>
        </form>

        <div style={styles.footer}>
          ¿No tienes cuenta?{' '}
          <button
            onClick={onSwitchToRegister}
            style={styles.link}
            disabled={loading}
          >
            Regístrate aquí
          </button>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    padding: '20px'
  },
  card: {
    background: 'white',
    borderRadius: '12px',
    padding: '40px',
    width: '100%',
    maxWidth: '400px',
    boxShadow: '0 20px 60px rgba(0,0,0,0.3)'
  },
  title: {
    margin: '0 0 8px 0',
    fontSize: '28px',
    fontWeight: '600',
    color: '#1a1a1a'
  },
  subtitle: {
    margin: '0 0 32px 0',
    color: '#666',
    fontSize: '14px'
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '20px'
  },
  error: {
    padding: '12px',
    background: '#fee',
    border: '1px solid #fcc',
    borderRadius: '6px',
    color: '#c33',
    fontSize: '14px'
  },
  inputGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px'
  },
  label: {
    fontSize: '14px',
    fontWeight: '500',
    color: '#333'
  },
  input: {
    padding: '12px',
    border: '1px solid #ddd',
    borderRadius: '6px',
    fontSize: '15px',
    transition: 'border-color 0.2s',
    outline: 'none'
  },
  button: {
    padding: '14px',
    fontSize: '16px',
    fontWeight: '600',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    background: '#667eea',
    color: 'white',
    transition: 'background 0.2s'
  },
  footer: {
    marginTop: '24px',
    textAlign: 'center',
    fontSize: '14px',
    color: '#666'
  },
  link: {
    background: 'none',
    border: 'none',
    color: '#667eea',
    cursor: 'pointer',
    textDecoration: 'underline',
    padding: 0,
    font: 'inherit'
  }
};
