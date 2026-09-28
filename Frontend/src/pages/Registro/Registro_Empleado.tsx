import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";

import "./Registro_Empleado.css";

const API_URL = "http://127.0.0.1:8000";

function RegistroEmpleado() {
  const navigate = useNavigate();

  const [codigoOrganizacion, setCodigoOrganizacion] = useState("");
  const [email, setEmail] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [confirmarContrasena, setConfirmarContrasena] = useState("");
  const [error, setError] = useState("");
  const [exito, setExito] = useState("");
  const [procesando, setProcesando] = useState(false);

  const manejarSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    setExito("");

    if (contrasena !== confirmarContrasena) {
      setError("Las contraseñas no coinciden.");
      return;
    }

    if (contrasena.length < 8) {
      setError("La contraseña debe tener al menos 8 caracteres.");
      return;
    }

    setProcesando(true);

    try {
      const respuesta = await fetch(`${API_URL}/auth/registro-empleado`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          codigo_organizacion: codigoOrganizacion.trim().toUpperCase(),
          email: email.trim(),
          contrasena,
        }),
      });

      if (!respuesta.ok) {
        let mensaje = "No fue posible completar el registro.";

        try {
          const data = await respuesta.json();
          if (data.detail) {
            mensaje =
              typeof data.detail === "string"
                ? data.detail
                : JSON.stringify(data.detail);
          }
        } catch {
          // mensaje por defecto
        }

        throw new Error(mensaje);
      }

      setExito("Cuenta creada correctamente. Ya puedes iniciar sesión.");
      setTimeout(() => {
        navigate("/login", { replace: true });
      }, 2000);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("No fue posible completar el registro.");
      }
    } finally {
      setProcesando(false);
    }
  };

  return (
    <main className="registro-page">
      <section className="registro-card">
        <div className="registro-header">
          <span className="registro-brand">FLOWOS</span>
          <h1>Registro de empleado</h1>
          <p>
            Ingresa el código de tu organización y el correo con el que estás
            registrado como empleado.
          </p>
        </div>

        <form onSubmit={manejarSubmit} className="registro-form">
          <div className="registro-field">
            <label htmlFor="codigo">Código de organización</label>
            <input
              id="codigo"
              type="text"
              value={codigoOrganizacion}
              onChange={(e) => setCodigoOrganizacion(e.target.value)}
              placeholder="Ej: FLOW-QMMK-VTH83"
              required
              autoComplete="off"
            />
          </div>

          <div className="registro-field">
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

          <div className="registro-field">
            <label htmlFor="contrasena">Contraseña</label>
            <input
              id="contrasena"
              type="password"
              value={contrasena}
              onChange={(e) => setContrasena(e.target.value)}
              placeholder="Mínimo 8 caracteres"
              required
              minLength={8}
              autoComplete="new-password"
            />
          </div>

          <div className="registro-field">
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

          {error && (
            <div className="registro-error" role="alert">
              {error}
            </div>
          )}

          {exito && (
            <div className="registro-exito" role="status">
              {exito}
            </div>
          )}

          <button
            type="submit"
            className="registro-button"
            disabled={procesando}
          >
            {procesando ? "Registrando..." : "Crear cuenta"}
          </button>
        </form>

        <div className="registro-footer">
          <span>¿Ya tienes cuenta?</span>
          <Link to="/login">Iniciar sesión</Link>
        </div>
      </section>
    </main>
  );
}

export default RegistroEmpleado;
