import { useEffect, useState, type FormEvent } from "react";

import {
  obtenerProyectos,
  obtenerEquipos,
  obtenerTareasPorProyecto,
  crearProyecto,
  type ProyectoCreate,
} from "../../service/api";

import { useAuth } from "../../context/AuthContext";
import { ROLES } from "../../utils/roles";

import type { Proyecto } from "../../types/proyecto";
import type { Equipo } from "../../types/equipo";
import type { Tarea } from "../../types/tarea";

import "./Proyectos.css";

const formVacio: ProyectoCreate = {
  nombre: "",
  descripcion: "",
  fecha_inicio: "",
  fecha_limite: "",
};

function Proyectos() {
  const { usuario } = useAuth();
  const esSecretario = usuario?.id_rol === ROLES.SECRETARIO;
  const esAdmin = usuario?.id_rol === ROLES.ADMIN;

  const [proyectos, setProyectos] = useState<Proyecto[]>([]);
  const [seleccionado, setSeleccionado] = useState<Proyecto | null>(null);
  const [equipos, setEquipos] = useState<Equipo[]>([]);
  const [tareas, setTareas] = useState<Tarea[]>([]);
  const [cargando, setCargando] = useState(true);
  const [cargandoDetalle, setCargandoDetalle] = useState(false);
  const [error, setError] = useState("");

  const [mostrarForm, setMostrarForm] = useState(false);
  const [form, setForm] = useState<ProyectoCreate>(formVacio);
  const [guardando, setGuardando] = useState(false);
  const [errorForm, setErrorForm] = useState("");

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
      const payload: ProyectoCreate = {
        nombre: form.nombre.trim(),
        descripcion: form.descripcion?.trim() || null,
        fecha_inicio: form.fecha_inicio,
        fecha_limite: form.fecha_limite,
      };

      if (payload.fecha_limite < payload.fecha_inicio) {
        throw new Error(
          "La fecha límite no puede ser anterior a la fecha de inicio.",
        );
      }

      const nuevo = await crearProyecto(payload);
      setProyectos((prev) => [nuevo, ...prev]);
      setSeleccionado(nuevo);
      setEquipos([]);
      setTareas([]);
      setMostrarForm(false);
      setForm(formVacio);
    } catch (err) {
      setErrorForm(
        err instanceof Error ? err.message : "No se pudo crear el proyecto",
      );
    } finally {
      setGuardando(false);
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
          <p>
            {esSecretario
              ? "Consulta proyectos, equipos y tareas de la organización."
              : "Crea y selecciona un proyecto para ver equipos, tareas e información. Luego usa OPTIMA para armar el equipo."}
          </p>
        </div>
        <div className="proy-hero-actions">
          <div className="proy-hero-stat">
            <strong>{proyectos.length}</strong>
            <span>registrados</span>
          </div>
          {esAdmin && (
            <button
              type="button"
              className="proy-btn-primary"
              onClick={abrirForm}
            >
              + Nuevo proyecto
            </button>
          )}
        </div>
      </div>

      <div className="proy-layout">
        <div className="proy-grid">
          {proyectos.length === 0 ? (
            <p className="proy-msg">
              {esAdmin
                ? "No hay proyectos. Crea el primero con “Nuevo proyecto”."
                : "No hay proyectos en esta organización."}
            </p>
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
                    <p className="proy-muted">
                      Sin tareas. Cuando existan, OPTIMA podrá proponer equipo.
                    </p>
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

      {mostrarForm && esAdmin && (
        <div className="proy-modal-overlay" onClick={cerrarForm}>
          <div
            className="proy-modal"
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
          >
            <div className="proy-modal-head">
              <h3>Nuevo proyecto</h3>
              <button type="button" onClick={cerrarForm} disabled={guardando}>
                ✕
              </button>
            </div>

            <form onSubmit={manejarSubmit} className="proy-form">
              <label>
                Nombre
                <input
                  required
                  maxLength={150}
                  value={form.nombre}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, nombre: e.target.value }))
                  }
                />
              </label>
              <label>
                Descripción
                <textarea
                  maxLength={500}
                  rows={3}
                  value={form.descripcion ?? ""}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, descripcion: e.target.value }))
                  }
                />
              </label>
              <label>
                Fecha inicio
                <input
                  type="date"
                  required
                  value={form.fecha_inicio}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, fecha_inicio: e.target.value }))
                  }
                />
              </label>
              <label>
                Fecha límite
                <input
                  type="date"
                  required
                  value={form.fecha_limite}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, fecha_limite: e.target.value }))
                  }
                />
              </label>

              {errorForm && <p className="proy-form-error">{errorForm}</p>}

              <div className="proy-form-actions">
                <button
                  type="button"
                  className="proy-btn-secondary"
                  onClick={cerrarForm}
                  disabled={guardando}
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="proy-btn-primary"
                  disabled={guardando}
                >
                  {guardando ? "Guardando..." : "Crear proyecto"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </section>
  );
}

export default Proyectos;
