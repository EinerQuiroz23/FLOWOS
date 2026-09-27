import { useState, type FormEvent } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { useAuth } from "../../context/AuthContext";

import "./Login.css";

function Login() {
  const { iniciarSesion, usuario, cargando } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [error, setError] = useState("");
  const [procesando, setProcesando] = useState(false);

  if (cargando) {
    return (
      <div className="login-loading">
        <div className="login-loading-spinner" />
        <span>Cargando FLOWOS...</span>
      </div>
    );
  }

  if (usuario) {
    return <Navigate to="/dashboard" replace />;
  }

  const manejarSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    setError("");
    setProcesando(true);

    try {
      await iniciarSesion(email, contrasena);
      navigate("/dashboard", { replace: true });
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError("No fue posible iniciar sesión.");
      }
    } finally {
      setProcesando(false);
    }
  };

  return (
    <main className="login-page">
      <section className="login-shell">
        {/* PANEL DE MARCA */}
        <div className="login-brand-panel">
          <div className="login-brand-content">
            <div className="login-brand-logo">
              <span>F</span>
            </div>

            <div className="login-brand-name">
              <strong>FLOWOS</strong>
              <span>Organizational OS</span>
            </div>

            <div className="login-brand-message">
              <span className="login-eyebrow">
                INTELLIGENT ORGANIZATIONAL PLATFORM
              </span>

              <h1>
                Organiza mejor.
                <br />
                <span>Decide mejor.</span>
              </h1>

              <p>
                Gestiona personas, proyectos, equipos y tareas desde una
                plataforma diseñada para optimizar la organización.
              </p>
            </div>

            <div className="login-optima">
              <div className="login-optima-mark">O</div>

              <div>
                <strong>OPTIMA ENGINE</strong>
                <span>Intelligent decision support</span>
              </div>
            </div>
          </div>

          <div className="login-brand-footer">
            <span>FLOWOS</span>
            <span>OPTIMA</span>
            <span>v1.0</span>
          </div>

          <div className="login-decoration login-decoration-one" />
          <div className="login-decoration login-decoration-two" />
          <div className="login-decoration login-decoration-three" />
        </div>

        {/* PANEL DEL FORMULARIO */}
        <div className="login-form-panel">
          <div className="login-form-container">
            <div className="login-form-header">
              <span className="login-mobile-brand">FLOWOS</span>

              <span className="login-form-eyebrow">ACCESO SEGURO</span>

              <h2>Bienvenido</h2>

              <p>Inicia sesión para acceder al panel de tu organización.</p>
            </div>

            <form onSubmit={manejarSubmit} className="login-form">
              <div className="login-field">
                <label htmlFor="email">Correo electrónico</label>

                <div className="login-input-wrapper">
                  <span className="login-input-icon">@</span>

                  <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    placeholder="tu@correo.com"
                    required
                    autoComplete="email"
                  />
                </div>
              </div>

              <div className="login-field">
                <div className="login-label-row">
                  <label htmlFor="contrasena">Contraseña</label>

                  <button
                    type="button"
                    className="login-forgot-button"
                    onClick={() => {
                      // Próximamente: recuperación de contraseña.
                    }}
                  >
                    ¿Olvidaste tu contraseña?
                  </button>
                </div>

                <div className="login-input-wrapper">
                  <span className="login-input-icon">●</span>

                  <input
                    id="contrasena"
                    type="password"
                    value={contrasena}
                    onChange={(event) => setContrasena(event.target.value)}
                    placeholder="Ingresa tu contraseña"
                    required
                    autoComplete="current-password"
                  />
                </div>
              </div>

              {error && (
                <div className="login-error" role="alert">
                  <span className="login-error-icon">!</span>
                  <span>{error}</span>
                </div>
              )}

              <button
                type="submit"
                className="login-button"
                disabled={procesando}
              >
                {procesando ? (
                  <>
                    <span className="login-button-spinner" />
                    Ingresando...
                  </>
                ) : (
                  <>
                    Iniciar sesión
                    <span className="login-button-arrow">→</span>
                  </>
                )}
              </button>
            </form>

            <div className="login-security">
              <span className="login-security-dot" />
              <span>Sesión protegida y autenticada</span>
            </div>

            <div className="login-form-footer">
              <span>FLOWOS</span>
              <span>•</span>
              <span>Organizational Optimization Platform</span>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}

export default Login;
