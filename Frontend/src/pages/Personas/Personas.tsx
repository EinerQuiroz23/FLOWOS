import { useEffect, useState } from "react";

import { obtenerPersonas } from "../../service/api";

import type { Persona } from "../../types/persona";

import "./Personas.css";

function Personas() {
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [seleccionada, setSeleccionada] = useState<Persona | null>(null);
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

  if (cargando) {
    return <div className="per-msg">Cargando personas...</div>;
  }

  if (error) {
    return <div className="per-error">{error}</div>;
  }

  // Carga semanal orientativa (0 hasta tener API de carga real)
  const horasUsadas = 0;
  const capacidad = Number(seleccionada?.capacidad_horas_semana ?? 0);
  const horasLibres = Math.max(capacidad - horasUsadas, 0);
  const pctUsado =
    capacidad > 0
      ? Math.min(100, Math.round((horasUsadas / capacidad) * 100))
      : 0;

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
        {/* LISTA */}
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

        {/* DETALLE */}
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
                <div className="per-hours-head">
                  <span>
                    {horasUsadas} h usadas · {horasLibres} h libres
                  </span>
                  <strong>{pctUsado}%</strong>
                </div>
                <div className="per-hours-bar">
                  <span style={{ width: `${pctUsado}%` }} />
                </div>
                <p className="per-hours-note">
                  Capacidad: {capacidad} h/semana.
                  {horasUsadas === 0 &&
                    " La carga real se conectará con las asignaciones activas."}
                </p>
              </div>
            </>
          )}
        </aside>
      </div>
    </section>
  );
}

export default Personas;
