import { useEffect, useState } from "react";

import {
  obtenerTareas,
  obtenerProyectos,
  obtenerEquipos,
} from "../../service/api";
import type { Tarea } from "../../types/tarea";
import type { Proyecto } from "../../types/proyecto";
import type { Equipo } from "../../types/equipo";

import "./Tareas.css";

function Tareas() {
  const [tareas, setTareas] = useState<Tarea[]>([]);
  const [proyectos, setProyectos] = useState<Proyecto[]>([]);
  const [equipos, setEquipos] = useState<Equipo[]>([]);
  const [seleccionada, setSeleccionada] = useState<Tarea | null>(null);
  const [filtro, setFiltro] = useState<string>("TODAS");
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const cargar = async () => {
      setCargando(true);
      setError("");
      try {
        const [t, p, e] = await Promise.all([
          obtenerTareas(),
          obtenerProyectos(),
          obtenerEquipos(),
        ]);
        setTareas(t);
        setProyectos(p);
        setEquipos(e);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "No se pudieron cargar las tareas",
        );
      } finally {
        setCargando(false);
      }
    };
    cargar();
  }, []);

  const nombreProyecto = (id: number) =>
    proyectos.find((p) => p.id_proyecto === id)?.nombre ?? `#${id}`;

  const nombreEquipo = (id: number) =>
    equipos.find((e) => e.id_equipo === id)?.nombre ?? `#${id}`;

  const tareasFiltradas =
    filtro === "TODAS"
      ? tareas
      : tareas.filter((t) => t.estado?.toUpperCase() === filtro);

  if (cargando) {
    return <div className="tar-msg">Cargando tareas...</div>;
  }

  if (error) {
    return <div className="tar-error">{error}</div>;
  }

  return (
    <section className="tar-page">
      <div className="tar-hero">
        <div>
          <span className="tar-eyebrow">TRABAJO</span>
          <h2>Tareas</h2>
          <p>
            Consulta y filtra las tareas de los proyectos de la organización.
          </p>
        </div>
        <div className="tar-hero-stat">
          <strong>{tareas.length}</strong>
          <span>total</span>
        </div>
      </div>

      <div className="tar-filters">
        {["TODAS", "PENDIENTE", "EN_PROGRESO", "FINALIZADA", "ASIGNADA"].map(
          (f) => (
            <button
              key={f}
              type="button"
              className={filtro === f ? "tar-filter active" : "tar-filter"}
              onClick={() => setFiltro(f)}
            >
              {f === "TODAS" ? "Todas" : f.replace("_", " ")}
            </button>
          ),
        )}
      </div>

      <div className="tar-layout">
        <div className="tar-list">
          {tareasFiltradas.length === 0 ? (
            <p className="tar-msg">No hay tareas con este filtro.</p>
          ) : (
            tareasFiltradas.map((tarea) => {
              const activa = seleccionada?.id_tarea === tarea.id_tarea;
              return (
                <article
                  key={tarea.id_tarea}
                  className={activa ? "tar-card active" : "tar-card"}
                  onClick={() => setSeleccionada(tarea)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") setSeleccionada(tarea);
                  }}
                >
                  <div className="tar-card-top">
                    <h3>{tarea.nombre}</h3>
                    <span
                      className={`tar-prio ${(tarea.prioridad || "").toLowerCase()}`}
                    >
                      {tarea.prioridad}
                    </span>
                  </div>
                  <p className="tar-desc">
                    {tarea.descripcion || "Sin descripción."}
                  </p>
                  <div className="tar-card-meta">
                    <span
                      className={`tar-estado ${(tarea.estado || "").toLowerCase()}`}
                    >
                      {tarea.estado}
                    </span>
                    <span>{tarea.fecha_limite}</span>
                    <span>{tarea.horas_estimadas} h</span>
                  </div>
                </article>
              );
            })
          )}
        </div>

        <aside className="tar-detail">
          {!seleccionada ? (
            <div className="tar-detail-empty">
              <span>✓</span>
              <p>Selecciona una tarea para ver el detalle.</p>
            </div>
          ) : (
            <>
              <span className="tar-eyebrow">DETALLE</span>
              <h2>{seleccionada.nombre}</h2>
              <div className="tar-detail-tags">
                <span
                  className={`tar-prio ${(seleccionada.prioridad || "").toLowerCase()}`}
                >
                  {seleccionada.prioridad}
                </span>
                <span
                  className={`tar-estado ${(seleccionada.estado || "").toLowerCase()}`}
                >
                  {seleccionada.estado}
                </span>
              </div>
              <p className="tar-desc">
                {seleccionada.descripcion || "Sin descripción."}
              </p>

              <div className="tar-detail-grid">
                <div>
                  <span>Proyecto</span>
                  <strong>{nombreProyecto(seleccionada.id_proyecto)}</strong>
                </div>
                <div>
                  <span>Equipo</span>
                  <strong>{nombreEquipo(seleccionada.id_equipo)}</strong>
                </div>
                <div>
                  <span>Horas estimadas</span>
                  <strong>{seleccionada.horas_estimadas} h</strong>
                </div>
                <div>
                  <span>Inicio</span>
                  <strong>{seleccionada.fecha_inicio}</strong>
                </div>
                <div>
                  <span>Límite</span>
                  <strong>{seleccionada.fecha_limite}</strong>
                </div>
                <div>
                  <span>ID tarea</span>
                  <strong>{seleccionada.id_tarea}</strong>
                </div>
              </div>
            </>
          )}
        </aside>
      </div>
    </section>
  );
}

export default Tareas;
