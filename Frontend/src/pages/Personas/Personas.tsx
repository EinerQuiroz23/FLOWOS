import { useEffect, useState } from "react";

import {
  obtenerPersonas,
  obtenerOcupacionPersona,
  type OcupacionPersona,
} from "../../service/api";

import type { Persona } from "../../types/persona";

import "./Personas.css";

function Personas() {
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [seleccionada, setSeleccionada] = useState<Persona | null>(null);
  const [ocupacion, setOcupacion] = useState<OcupacionPersona | null>(null);
  const [cargandoOcupacion, setCargandoOcupacion] = useState(false);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const cargar = async () => {
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
    cargar();
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
        <div className="per-hero-stat">
          <strong>{personas.length}</strong>
          <span>registradas</span>
        </div>
      </div>

      <div className="per-layout">
        <div className="per-grid">
          {personas.length === 0 ? (
            <p className="per-msg">No hay personas registradas.</p>
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
    </section>
  );
}

export default Personas;
