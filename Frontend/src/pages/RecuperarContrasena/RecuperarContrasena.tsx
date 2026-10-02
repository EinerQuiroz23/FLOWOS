import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";

import "./RecuperarContrasena.css";

const API_URL = "http://127.0.0.1:8000";

type Paso = "solicitar" | "restablecer";

function RecuperarContrasena() {
  const navigate = useNavigate();

  const [paso, setPaso] = useState<Paso>("solicitar");
  const [email, setEmail] = useState("");
  const [codigo, setCodigo] = useState("");
  const [nuevaContrasena, setNuevaContrasena] = useState("");
  const [confirmarContrasena, setConfirmarContrasena] = useState("");
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [procesando, setProcesando] = useState(false);

  const solicitarCodigo = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    setMensaje("");
    setProcesando(true);

    try {
      const respuesta = await fetch(
        `${API_URL}/auth/recuperar-contrasena/solicitar`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: email.trim() }),
        },
      );

      if (!respuesta.ok) {
        let msg = "No se pudo enviar el código.";
        try {
          const data = await respuesta.json();
          if (data.detail) msg = String(data.detail);
        } catch {
          // default
        }
        throw new Error(msg);
      }

      setMensaje(
        "Si el correo existe, te enviamos un código de 6 dígitos. Revisa tu bandeja y spam.",
      );
      setPaso("restablecer");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Error al solicitar el código.",
      );
    } finally {
      setProcesando(false);
    }
  };

  const restablecer = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    setMensaje("");

    if (nuevaContrasena !== confirmarContrasena) {
      setError("Las contraseñas no coinciden.");
      return;
    }

    if (nuevaContrasena.length < 8) {
      setError("La contraseña debe tener al menos 8 caracteres.");
      return;
    }

    if (!/^\d{6}$/.test(codigo.trim())) {
      setError("El código debe ser de 6 dígitos.");
      return;
    }

    setProcesando(true);

    try {
      const respuesta = await fetch(
        `${API_URL}/auth/recuperar-contrasena/restablecer`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email: email.trim(),
            codigo: codigo.trim(),
            nueva_contrasena: nuevaContrasena,
          }),
        },
      );

      if (!respuesta.ok) {
        let msg = "No se pudo restablecer la contraseña.";
        try {
          const data = await respuesta.json();
          if (data.detail) msg = String(data.detail);
        } catch {
          // default
        }
        throw new Error(msg);
      }

      setMensaje("Contraseña actualizada. Redirigiendo al login...");
      setTimeout(() => navigate("/login", { replace: true }), 2000);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Error al restablecer la contraseña.",
      );
    } finally {
      setProcesando(false);
    }
  };

  return (
    <main className="recuperar-page">
      <section className="recuperar-card">
        <div className="recuperar-header">
          <span className="recuperar-brand">FLOWOS</span>
          <h1>Recuperar contraseña</h1>
          <p>
            {paso === "solicitar"
              ? "Ingresa tu correo y te enviaremos un código de verificación."
              : "Ingresa el código de 6 dígitos y tu nueva contraseña."}
          </p>
        </div>

        {paso === "solicitar" ? (
          <form onSubmit={solicitarCodigo} className="recuperar-form">
            <div className="recuperar-field">
              <label htmlFor="email">Correo electrónico</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="tu@correo.com"
                required
                autoComplete="email"
              />
            </div>

            {error && <div className="recuperar-error">{error}</div>}
            {mensaje && <div className="recuperar-exito">{mensaje}</div>}

            <button
              type="submit"
              className="recuperar-button"
              disabled={procesando}
            >
              {procesando ? "Enviando..." : "Enviar código"}
            </button>
          </form>
        ) : (
          <form onSubmit={restablecer} className="recuperar-form">
            <div className="recuperar-field">
              <label htmlFor="email2">Correo</label>
              <input id="email2" type="email" value={email} disabled />
            </div>

            <div className="recuperar-field">
              <label htmlFor="codigo">Código de 6 dígitos</label>
              <input
                id="codigo"
                type="text"
                inputMode="numeric"
                maxLength={6}
                value={codigo}
                onChange={(e) => setCodigo(e.target.value.replace(/\D/g, ""))}
                placeholder="000000"
                required
              />
            </div>

            <div className="recuperar-field">
              <label htmlFor="nueva">Nueva contraseña</label>
              <input
                id="nueva"
                type="password"
                value={nuevaContrasena}
                onChange={(e) => setNuevaContrasena(e.target.value)}
                placeholder="Mínimo 8 caracteres"
                required
                minLength={8}
                autoComplete="new-password"
              />
            </div>

            <div className="recuperar-field">
              <label htmlFor="confirmar">Confirmar contraseña</label>
              <input
                id="confirmar"
                type="password"
                value={confirmarContrasena}
                onChange={(e) => setConfirmarContrasena(e.target.value)}
                placeholder="Repite la contraseña"
                required
                minLength={8}
                autoComplete="new-password"
              />
            </div>

            {error && <div className="recuperar-error">{error}</div>}
            {mensaje && <div className="recuperar-exito">{mensaje}</div>}

            <button
              type="submit"
              className="recuperar-button"
              disabled={procesando}
            >
              {procesando ? "Guardando..." : "Restablecer contraseña"}
            </button>

            <button
              type="button"
              className="recuperar-link-button"
              onClick={() => {
                setPaso("solicitar");
                setCodigo("");
                setError("");
                setMensaje("");
              }}
            >
              Volver a pedir código
            </button>
          </form>
        )}

        <div className="recuperar-footer">
          <Link to="/login">Volver al login</Link>
        </div>
      </section>
    </main>
  );
}

export default RecuperarContrasena;
