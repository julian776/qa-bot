import { useState } from 'react';
import LoginForm from '../components/LoginForm';
import RegisterForm from '../components/RegisterForm';
import { useAuth } from '../contexts/AuthContext';

export default function AuthPage() {
  const [mode, setMode] = useState('login'); // 'login' or 'register'
  const { login, register } = useAuth();

  return (
    <>
      {mode === 'login' ? (
        <LoginForm
          onLogin={login}
          onSwitchToRegister={() => setMode('register')}
        />
      ) : (
        <RegisterForm
          onRegister={register}
          onSwitchToLogin={() => setMode('login')}
        />
      )}
    </>
  );
}
