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
      setSeleccionada(nueva);
      setMostrarForm(false);
      setForm(formVacio);
    } catch (err) {
      setErrorForm(
        err instanceof Error ? err.message : "No se pudo crear la persona",
      );
    } finally {
      setGuardando(false);
    }
  };

  if (cargando) {
    return <div className="per-msg">Cargando personas...</div>;
  }

  if (error) {
    return <div className="per-error">{error}</div>;
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
      <div className="per-hero">
        <div>
          <span className="per-eyebrow">TALENTO</span>
          <h2>Personas</h2>
          <p>
            Consulta el equipo de la organización y el detalle de cada perfil.
          </p>
        </div>
        <div className="per-hero-actions">
          <div className="per-hero-stat">
            <strong>{personas.length}</strong>
            <span>registradas</span>
          </div>
          <button type="button" className="per-btn-primary" onClick={abrirForm}>
            + Nueva persona
          </button>
        </div>
      </div>

      <div className="per-layout">
        <div className="per-grid">
          {personas.length === 0 ? (
            <p className="per-msg">
              No hay personas. Crea la primera con “Nueva persona”.
            </p>
          ) : (
            personas.map((persona) => {
              const activa = seleccionada?.id_persona === persona.id_persona;
              return (
                <article
                  key={persona.id_persona}
                  className={activa ? "per-card active" : "per-card"}
                  onClick={() => setSeleccionada(persona)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") setSeleccionada(persona);
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
                        {persona.estado ? "ACTIVO" : "INACTIVO"}
                      </span>
                    </div>
                  </div>
                  <p className="per-email">{persona.email}</p>
                  <div className="per-card-meta">
                    <span>{persona.capacidad_horas_semana} h/sem</span>
                    {persona.telefono && <span>{persona.telefono}</span>}
                  </div>
                </article>
              );
            })
          )}
        </div>

        <aside className="per-detail">
          {!seleccionada ? (
            <div className="per-detail-empty">
              <span>♙</span>
              <p>Haz clic en una persona para ver su información.</p>
            </div>
          ) : (
            <>
              <div className="per-detail-header">
                <div className="per-avatar lg">
                  {seleccionada.nombre.charAt(0)}
                  {seleccionada.apellido.charAt(0)}
                </div>
                <div>
                  <span className="per-eyebrow">PERFIL</span>
                  <h2>
                    {seleccionada.nombre} {seleccionada.apellido}
                  </h2>
                  <span
                    className={
                      seleccionada.estado ? "per-badge on" : "per-badge off"
                    }
                  >
                    {seleccionada.estado ? "ACTIVO" : "INACTIVO"}
                  </span>
                </div>
              </div>

              <div className="per-detail-block">
                <h3>Contacto</h3>
                <div className="per-contact">
                  <div>
                    <span>Correo</span>
                    <strong>{seleccionada.email}</strong>
                  </div>
                  <div>
                    <span>Teléfono</span>
                    <strong>{seleccionada.telefono || "—"}</strong>
                  </div>
                  <div>
                    <span>ID persona</span>
                    <strong>{seleccionada.id_persona}</strong>
                  </div>
                </div>
              </div>

              <div className="per-detail-block">
                <h3>Carga semanal</h3>
                {cargandoOcupacion ? (
                  <p className="per-hours-note">Calculando ocupación...</p>
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
            </>
          )}
        </aside>
      </div>

      {/* MODAL NUEVA PERSONA */}
      {mostrarForm && (
        <div className="per-modal-overlay" onClick={cerrarForm}>
          <div
            className="per-modal"
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
          >
            <div className="per-modal-head">
              <h3>Nueva persona</h3>
              <button type="button" onClick={cerrarForm} disabled={guardando}>
                ✕
              </button>
            </div>

            <form onSubmit={manejarSubmit} className="per-form">
              <label>
                Nombre
                <input
                  required
                  value={form.nombre}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, nombre: e.target.value }))
                  }
                />
              </label>
              <label>
                Apellido
                <input
                  required
                  value={form.apellido}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, apellido: e.target.value }))
                  }
                />
              </label>
              <label>
                Email
                <input
                  type="email"
                  required
                  value={form.email}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, email: e.target.value }))
                  }
                />
              </label>
              <label>
                Teléfono
                <input
                  value={form.telefono ?? ""}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, telefono: e.target.value }))
                  }
                />
              </label>
              <label>
                Capacidad (h/semana)
                <input
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
              </label>

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
