import { useEffect, useState } from "react";

import {
  obtenerProyectos,
  obtenerEquipos,
  obtenerTareasPorProyecto,
} from "../../service/api";

import type { Proyecto } from "../../types/proyecto";
import type { Equipo } from "../../types/equipo";
import type { Tarea } from "../../types/tarea";

import "./Proyectos.css";

function Proyectos() {
  const [proyectos, setProyectos] = useState<Proyecto[]>([]);
  const [seleccionado, setSeleccionado] = useState<Proyecto | null>(null);
  const [equipos, setEquipos] = useState<Equipo[]>([]);
  const [tareas, setTareas] = useState<Tarea[]>([]);
  const [cargando, setCargando] = useState(true);
  const [cargandoDetalle, setCargandoDetalle] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const cargar = async () => {
      setCargando(true);
      setError("");
      try {
        const datos = await obtenerProyectos();
        setProyectos(datos);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "No se pudieron cargar proyectos",
        );
      } finally {
        setCargando(false);
      }
    };
    cargar();
  }, []);

  const abrirDetalle = async (proyecto: Proyecto) => {
    setSeleccionado(proyecto);
    setCargandoDetalle(true);
    setEquipos([]);
    setTareas([]);

    try {
      const [todosEquipos, tareasProyecto] = await Promise.all([
        obtenerEquipos(),
        obtenerTareasPorProyecto(proyecto.id_proyecto),
      ]);

      setEquipos(
        todosEquipos.filter((e) => e.id_proyecto === proyecto.id_proyecto),
      );
      setTareas(tareasProyecto);
    } catch (err) {
      console.error(err);
    } finally {
      setCargandoDetalle(false);
    }
  };

  if (cargando) {
    return <div className="proy-msg">Cargando proyectos...</div>;
  }

  if (error) {
    return <div className="proy-error">{error}</div>;
  }

  return (
    <section className="proy-page">
      <div className="proy-hero">
        <div>
          <span className="proy-eyebrow">GESTIÓN</span>
          <h2>Proyectos</h2>
          <p>Selecciona un proyecto para ver equipos, tareas e información.</p>
        </div>
        <div className="proy-hero-stat">
          <strong>{proyectos.length}</strong>
          <span>registrados</span>
        </div>
      </div>

      <div className="proy-layout">
        {/* LISTA */}
        <div className="proy-grid">
          {proyectos.length === 0 ? (
            <p className="proy-msg">No hay proyectos en esta organización.</p>
          ) : (
            proyectos.map((proyecto) => {
              const activo = seleccionado?.id_proyecto === proyecto.id_proyecto;
              return (
                <article
                  key={proyecto.id_proyecto}
                  className={activo ? "proy-card active" : "proy-card"}
                  onClick={() => abrirDetalle(proyecto)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") abrirDetalle(proyecto);
                  }}
                >
                  <div className="proy-card-top">
                    <h3>{proyecto.nombre}</h3>
                    <span
                      className={`proy-badge ${proyecto.estado
                        .toLowerCase()
                        .replace(/\s/g, "-")}`}
                    >
                      {proyecto.estado}
                    </span>
                  </div>
                  <p className="proy-desc">
                    {proyecto.descripcion || "Sin descripción."}
                  </p>
                  <div className="proy-dates">
                    <span>{proyecto.fecha_inicio}</span>
                    <span>→</span>
                    <span>{proyecto.fecha_limite}</span>
                  </div>
                </article>
              );
            })
          )}
        </div>

        {/* DETALLE */}
        <aside className="proy-detail">
          {!seleccionado ? (
            <div className="proy-detail-empty">
              <span>▣</span>
              <p>Haz clic en un proyecto para ver el detalle.</p>
            </div>
          ) : (
            <>
              <span className="proy-eyebrow">DETALLE</span>
              <h2>{seleccionado.nombre}</h2>
              <span
                className={`proy-badge ${seleccionado.estado
                  .toLowerCase()
                  .replace(/\s/g, "-")}`}
              >
                {seleccionado.estado}
              </span>
              <p className="proy-detail-desc">
                {seleccionado.descripcion || "Sin descripción."}
              </p>

              <div className="proy-detail-meta">
                <div>
                  <span>Inicio</span>
                  <strong>{seleccionado.fecha_inicio}</strong>
                </div>
                <div>
                  <span>Límite</span>
                  <strong>{seleccionado.fecha_limite}</strong>
                </div>
                <div>
                  <span>ID</span>
                  <strong>{seleccionado.id_proyecto}</strong>
                </div>
              </div>

              {cargandoDetalle ? (
                <p className="proy-msg">Cargando equipos y tareas...</p>
              ) : (
                <>
                  <h3 className="proy-section-title">
                    Equipos ({equipos.length})
                  </h3>
                  {equipos.length === 0 ? (
                    <p className="proy-muted">Sin equipos en este proyecto.</p>
                  ) : (
                    <ul className="proy-list">
                      {equipos.map((e) => (
                        <li key={e.id_equipo}>
                          <strong>{e.nombre}</strong>
                          <span>{e.estado}</span>
                        </li>
                      ))}
                    </ul>
                  )}

                  <h3 className="proy-section-title">
                    Tareas ({tareas.length})
                  </h3>
                  {tareas.length === 0 ? (
                    <p className="proy-muted">Sin tareas registradas.</p>
                  ) : (
                    <ul className="proy-list">
                      {tareas.map((t) => (
                        <li key={t.id_tarea}>
                          <strong>{t.nombre}</strong>
                          <span>
                            {t.estado} · {t.prioridad}
                          </span>
                        </li>
                      ))}
                    </ul>
                  )}
                </>
              )}
            </>
          )}
        </aside>
      </div>
    </section>
  );
}

export default Proyectos;
