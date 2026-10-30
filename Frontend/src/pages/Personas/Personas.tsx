import { useEffect, useState, type FormEvent } from "react";

import {
  obtenerPersonas,
  obtenerOcupacionPersona,
  crearPersona,
  type OcupacionPersona,
  type PersonaCreate,
} from "../../service/api";

import type { Persona } from "../../types/persona";

import "./Personas.css";

const formVacio: PersonaCreate = {
  nombre: "",
  apellido: "",
  email: "",
  telefono: "",
  capacidad_horas_semana: 40,
};

function Personas() {
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [seleccionada, setSeleccionada] = useState<Persona | null>(null);
  const [ocupacion, setOcupacion] = useState<OcupacionPersona | null>(null);
  const [cargandoOcupacion, setCargandoOcupacion] = useState(false);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  const [mostrarForm, setMostrarForm] = useState(false);
  const [form, setForm] = useState<PersonaCreate>(formVacio);
  const [guardando, setGuardando] = useState(false);
  const [errorForm, setErrorForm] = useState("");

  const cargarPersonas = async () => {
    setCargando(true);
    setError("");
    try {
      const datos = await obtenerPersonas();
      setPersonas(datos);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "No se pudieron cargar personas",
      );
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarPersonas();
  }, []);

  useEffect(() => {
    if (!seleccionada) {
      setOcupacion(null);
      return;
    }

    let cancelado = false;

    const cargarOcupacion = async () => {
      setCargandoOcupacion(true);
      try {
        const data = await obtenerOcupacionPersona(seleccionada.id_persona);
        if (!cancelado) setOcupacion(data);
      } catch {
        if (!cancelado) {
          setOcupacion({
            id_persona: seleccionada.id_persona,
            capacidad_horas_semana: Number(
              seleccionada.capacidad_horas_semana ?? 0,
            ),
            ocupacion_pct: 0,
            disponibilidad_pct: 100,
          });
        }
      } finally {
        if (!cancelado) setCargandoOcupacion(false);
      }
    };

    cargarOcupacion();

    return () => {
      cancelado = true;
    };
  }, [seleccionada]);

  const cerrarDetalle = () => setSeleccionada(null);

  const abrirForm = () => {
    setForm(formVacio);
    setErrorForm("");
    setMostrarForm(true);
  };

  const cerrarForm = () => {
    if (guardando) return;
    setMostrarForm(false);
    setErrorForm("");
  };

  const manejarSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setErrorForm("");
    setGuardando(true);

    try {
      const payload: PersonaCreate = {
        nombre: form.nombre.trim(),
        apellido: form.apellido.trim(),
        email: form.email.trim(),
        telefono: form.telefono?.trim() || null,
        capacidad_horas_semana: Number(form.capacidad_horas_semana),
      };

      const nueva = await crearPersona(payload);
      setPersonas((prev) => [...prev, nueva]);
      setMostrarForm(false);
      setForm(formVacio);
      setSeleccionada(nueva);
    } catch (err) {
      setErrorForm(
        err instanceof Error ? err.message : "No se pudo crear la persona",
      );
    } finally {
      setGuardando(false);
    }
  };

  if (cargando) {
    return (
      <div className="per-state">
        <div className="per-spinner" />
        <p>Cargando personas...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="per-state per-state-error">
        <p>{error}</p>
      </div>
    );
  }

  const capacidad = Number(
    ocupacion?.capacidad_horas_semana ??
      seleccionada?.capacidad_horas_semana ??
      0,
  );
  const ocupacionPct = Number(ocupacion?.ocupacion_pct ?? 0);
  const disponibilidadPct = Number(
    ocupacion?.disponibilidad_pct ?? Math.max(0, 100 - ocupacionPct),
  );
  const pctBarra = Math.min(100, Math.round(ocupacionPct));

  return (
    <section className="per-page">
      <header className="per-header">
        <div className="per-header-text">
          <span className="per-kicker">Talento</span>
          <h1>Personas</h1>
          <p>
            Consulta el equipo de la organización y el detalle de cada perfil.
          </p>
        </div>
        <div className="per-header-actions">
          <div className="per-count">
            <strong>{personas.length}</strong>
            <span>registradas</span>
          </div>
          <button type="button" className="per-btn-primary" onClick={abrirForm}>
            <span className="per-btn-icon">+</span>
            Nueva persona
          </button>
        </div>
      </header>

      {personas.length === 0 ? (
        <div className="per-empty">
          <div className="per-empty-icon">♙</div>
          <h3>Sin personas</h3>
          <p>Crea la primera con el botón “Nueva persona”.</p>
          <button type="button" className="per-btn-primary" onClick={abrirForm}>
            + Nueva persona
          </button>
        </div>
      ) : (
        <div className="per-grid">
          {personas.map((persona) => (
            <article
              key={persona.id_persona}
              className="per-card"
              onClick={() => setSeleccionada(persona)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  setSeleccionada(persona);
                }
              }}
            >
              <div className="per-card-top">
                <div className="per-avatar">
                  {persona.nombre.charAt(0)}
                  {persona.apellido.charAt(0)}
                </div>
                <div className="per-card-info">
                  <h3>
                    {persona.nombre} {persona.apellido}
                  </h3>
                  <span
                    className={
                      persona.estado ? "per-badge on" : "per-badge off"
                    }
                  >
                    {persona.estado ? "Activo" : "Inactivo"}
                  </span>
                </div>
              </div>
              <p className="per-email">{persona.email}</p>
              <div className="per-card-footer">
                <span>{persona.capacidad_horas_semana} h/sem</span>
                <span className="per-card-hint">Ver perfil</span>
              </div>
            </article>
          ))}
        </div>
      )}

      {seleccionada && (
        <div className="per-overlay" onClick={cerrarDetalle}>
          <div
            className="per-modal"
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
          >
            <div className="per-modal-head">
              <div className="per-modal-identity">
                <div className="per-avatar lg">
                  {seleccionada.nombre.charAt(0)}
                  {seleccionada.apellido.charAt(0)}
                </div>
                <div>
                  <span className="per-kicker">Perfil</span>
                  <h2>
                    {seleccionada.nombre} {seleccionada.apellido}
                  </h2>
                  <span
                    className={
                      seleccionada.estado ? "per-badge on" : "per-badge off"
                    }
                  >
                    {seleccionada.estado ? "Activo" : "Inactivo"}
                  </span>
                </div>
              </div>
              <button
                type="button"
                className="per-modal-close"
                onClick={cerrarDetalle}
                aria-label="Cerrar"
              >
                ✕
              </button>
            </div>

            <div className="per-modal-body">
              <h3>Contacto</h3>
              <div className="per-meta-grid">
                <div className="per-meta-item">
                  <span>Correo</span>
                  <strong>{seleccionada.email}</strong>
                </div>
                <div className="per-meta-item">
                  <span>Teléfono</span>
                  <strong>{seleccionada.telefono || "—"}</strong>
                </div>
                <div className="per-meta-item">
                  <span>ID</span>
                  <strong>#{seleccionada.id_persona}</strong>
                </div>
              </div>

              <h3>Carga semanal</h3>
              {cargandoOcupacion ? (
                <div className="per-detail-loading">
                  <div className="per-spinner" />
                  <p>Calculando ocupación...</p>
                </div>
              ) : (
                <>
                  <div className="per-hours-head">
                    <span>
                      Ocupación {ocupacionPct.toFixed(0)}% · Libre{" "}
                      {disponibilidadPct.toFixed(0)}%
                    </span>
                    <strong>{pctBarra}%</strong>
                  </div>
                  <div className="per-hours-bar">
                    <span
                      style={{
                        width: `${pctBarra}%`,
                        background:
                          pctBarra >= 100
                            ? "#dc2626"
                            : pctBarra >= 70
                              ? "#f59e0b"
                              : "#16a34a",
                      }}
                    />
                  </div>
                  <p className="per-hours-note">
                    Capacidad: {capacidad} h/semana. La ocupación suma el % de
                    dedicación de tareas ASIGNADA / EN_PROGRESO (misma lógica
                    que OPTIMA).
                  </p>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {mostrarForm && (
        <div className="per-overlay" onClick={cerrarForm}>
          <div
            className="per-modal per-modal-form"
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
          >
            <div className="per-modal-head">
              <div>
                <span className="per-kicker">Nuevo</span>
                <h2>Crear persona</h2>
              </div>
              <button
                type="button"
                className="per-modal-close"
                onClick={cerrarForm}
                disabled={guardando}
                aria-label="Cerrar"
              >
                ✕
              </button>
            </div>

            <form onSubmit={manejarSubmit} className="per-form">
              <div className="per-form-row">
                <div className="per-form-group">
                  <label htmlFor="per-nombre">Nombre</label>
                  <input
                    id="per-nombre"
                    required
                    value={form.nombre}
                    onChange={(e) =>
                      setForm((f) => ({ ...f, nombre: e.target.value }))
                    }
                  />
                </div>
                <div className="per-form-group">
                  <label htmlFor="per-apellido">Apellido</label>
                  <input
                    id="per-apellido"
                    required
                    value={form.apellido}
                    onChange={(e) =>
                      setForm((f) => ({ ...f, apellido: e.target.value }))
                    }
                  />
                </div>
              </div>
              <div className="per-form-group">
                <label htmlFor="per-email">Email</label>
                <input
                  id="per-email"
                  type="email"
                  required
                  value={form.email}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, email: e.target.value }))
                  }
                />
              </div>
              <div className="per-form-row">
                <div className="per-form-group">
                  <label htmlFor="per-tel">Teléfono</label>
                  <input
                    id="per-tel"
                    maxlength={11}
                    value={form.telefono ?? ""}
                    onChange={(e) =>
                      setForm((f) => ({ ...f, telefono: e.target.value }))
                    }
                  />
                </div>
                <div className="per-form-group">
                  <label htmlFor="per-horas">Capacidad (h/semana)</label>
                  <input
                    id="per-horas"
                    type="number"
                    min={1}
                    max={168}
                    step={0.5}
                    required
                    value={form.capacidad_horas_semana}
                    onChange={(e) =>
                      setForm((f) => ({
                        ...f,
                        capacidad_horas_semana: Number(e.target.value),
                      }))
                    }
                  />
                </div>
              </div>

              {errorForm && <p className="per-form-error">{errorForm}</p>}

              <div className="per-form-actions">
                <button
                  type="button"
                  className="per-btn-secondary"
                  onClick={cerrarForm}
                  disabled={guardando}
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="per-btn-primary"
                  disabled={guardando}
                >
                  {guardando ? "Guardando..." : "Crear persona"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </section>
  );
}

export default Personas;
