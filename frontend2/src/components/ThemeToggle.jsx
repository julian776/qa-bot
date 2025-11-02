import { useEffect, useState } from "react";

export default function ThemeToggle() {
  const [dark, setDark] = useState(true);
  useEffect(() => {
    document.documentElement.style.setProperty("color-scheme", dark ? "dark" : "light");
  }, [dark]);
  return (
    <button className="btn" onClick={() => setDark(d => !d)} aria-label="Cambiar tema">
      {dark ? "🌙 Oscuro" : "☀️ Claro"}
    </button>
  );
}
