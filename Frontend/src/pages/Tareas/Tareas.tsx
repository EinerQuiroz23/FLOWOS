import { useEffect, useMemo, useState, type FormEvent } from "react";

import {
  obtenerTareas,
  obtenerProyectos,
  obtenerEquipos,
  obtenerHabilidades,
  obtenerNivelesHabilidad,
  crearTarea,
  type TareaCreate,
} from "../../service/api";
import { useAuth } from "../../context/AuthContext";
import { ROLES } from "../../utils/roles";
import type { Tarea } from "../../types/tarea";
import type { Proyecto } from "../../types/proyecto";
import type { Equipo } from "../../types/equipo";

import "./Tareas.css";

type HabReq = {
  id_tarea_habilidad: number;
  id_tarea: number;
  id_habilidad: number;
  id_nivel: number;
};

type HabCatalogo = {
  id_habilidad: number;
  nombre: string;
  estado?: boolean | null;
};
type NivelCat = { id_nivel: number; nombre: string };

const API = "http://127.0.0.1:8000";

function soloFecha(valor?: string | null): string {
  if (!valor) return "";
  return valor.slice(0, 10);
}

async function apiHab<T>(ruta: string, opciones?: RequestInit): Promise<T> {
  const token = sessionStorage.getItem("flowos_token");
  const respuesta = await fetch(`${API}${ruta}`, {
    ...opciones,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
  if (!respuesta.ok) {
    const error = await respuesta.json().catch(() => null);
    const detalle = error?.detail;
    const mensaje = Array.isArray(detalle)
      ? detalle.map((item: { msg?: string }) => item.msg || "").join(", ")
      : detalle || "No se pudo guardar la habilidad";
    throw new Error(
      typeof mensaje === "string" ? mensaje : "No se pudo guardar la habilidad",
    );
  }
  if (respuesta.status === 204) return undefined as T;
  return respuesta.json();
}

const formVacio: TareaCreate = {
  id_proyecto: 0,
  id_equipo: 0,
  nombre: "",
  descripcion: "",
  prioridad: "MEDIA",
  horas_estimadas: 8,
  fecha_inicio: "",
  fecha_limite: "",
};

function Tareas() {
  const { usuario } = useAuth();
  const puedeCrear =
    usuario?.id_rol === ROLES.ADMIN || usuario?.id_rol === ROLES.SECRETARIO;

  const [tareas, setTareas] = useState<Tarea[]>([]);
  const [proyectos, setProyectos] = useState<Proyecto[]>([]);
  const [equipos, setEquipos] = useState<Equipo[]>([]);
  const [seleccionada, setSeleccionada] = useState<Tarea | null>(null);
  const [filtro, setFiltro] = useState<string>("TODAS");
  const [proyectoFiltro, setProyectoFiltro] = useState<number | "TODOS">(
    "TODOS",
  );
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  const [mostrarForm, setMostrarForm] = useState(false);
  const [editId, setEditId] = useState<number | null>(null);
  const [form, setForm] = useState<TareaCreate>(formVacio);
  const [guardando, setGuardando] = useState(false);
  const [errorForm, setErrorForm] = useState("");

  const [habilidades, setHabilidades] = useState<HabCatalogo[]>([]);
  const [niveles, setNiveles] = useState<NivelCat[]>([]);
  const [reqs, setReqs] = useState<HabReq[]>([]);
  const [idHab, setIdHab] = useState("");
  const [idNivel, setIdNivel] = useState("");
  const [guardandoHab, setGuardandoHab] = useState(false);
  const [errorHab, setErrorHab] = useState("");

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
        const [habs, nivs] = await Promise.all([
          obtenerHabilidades(),
          obtenerNivelesHabilidad(),
        ]);
        setHabilidades(habs.filter((h) => h.estado !== false));
        setNiveles(nivs);
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

  useEffect(() => {
    if (!seleccionada) {
      setReqs([]);
      return;
    }
    apiHab<HabReq[]>(`/tareas-habilidades/tarea/${seleccionada.id_tarea}`)
      .then(setReqs)
      .catch(() => setReqs([]));
  }, [seleccionada]);

  const equiposDelProyecto = useMemo(() => {
    if (!form.id_proyecto) return [];
    return equipos.filter((e) => e.id_proyecto === form.id_proyecto);
  }, [equipos, form.id_proyecto]);

  const nombreProyecto = (id: number) =>
    proyectos.find((p) => p.id_proyecto === id)?.nombre ?? `#${id}`;

  const nombreEquipo = (id: number) =>
    equipos.find((e) => e.id_equipo === id)?.nombre ?? `#${id}`;

  const tareasFiltradas = tareas.filter((t) => {
    const porProyecto =
      proyectoFiltro === "TODOS" || t.id_proyecto === proyectoFiltro;
    const porEstado = filtro === "TODAS" || t.estado?.toUpperCase() === filtro;
    return porProyecto && porEstado;
  });

  const abrirForm = () => {
    setSeleccionada(null);
    setEditId(null);
    setForm({
      ...formVacio,
      id_proyecto:
        proyectoFiltro === "TODOS"
          ? (proyectos[0]?.id_proyecto ?? 0)
          : proyectoFiltro,
      id_equipo: 0,
    });
    setErrorForm("");
    setMostrarForm(true);
  };

  const abrirEdicion = () => {
    if (!seleccionada) return;
    setEditId(seleccionada.id_tarea);
    setForm({
      id_proyecto: seleccionada.id_proyecto,
      id_equipo: seleccionada.id_equipo,
      nombre: seleccionada.nombre,
      descripcion: seleccionada.descripcion ?? "",
      prioridad: seleccionada.prioridad || "MEDIA",
      horas_estimadas: seleccionada.horas_estimadas,
      fecha_inicio: soloFecha(seleccionada.fecha_inicio),
      fecha_limite: soloFecha(seleccionada.fecha_limite),
    });
    setErrorForm("");
    setMostrarForm(true);
  };

  const nombreHab = (id: number) =>
    habilidades.find((h) => h.id_habilidad === id)?.nombre ??
    `Habilidad #${id}`;

  const nombreNivel = (id: number) =>
    niveles.find((n) => n.id_nivel === id)?.nombre ?? `Nivel #${id}`;

  const agregarHabilidad = async () => {
    if (!seleccionada || !idHab || !idNivel) return;
    setGuardandoHab(true);
    setErrorHab("");
    try {
      const nueva = await apiHab<HabReq>("/tareas-habilidades/", {
        method: "POST",
        body: JSON.stringify({
          id_tarea: seleccionada.id_tarea,
          id_habilidad: Number(idHab),
          id_nivel: Number(idNivel),
        }),
      });
      setReqs((prev) => [...prev, nueva]);
      setIdHab("");
      setIdNivel("");
    } catch (err) {
      setErrorHab(
        err instanceof Error ? err.message : "No se pudo agregar la habilidad",
      );
    } finally {
      setGuardandoHab(false);
    }
  };

  const quitarHabilidad = async (id: number) => {
    setErrorHab("");
    try {
      await apiHab(`/tareas-habilidades/${id}`, { method: "DELETE" });
      setReqs((prev) => prev.filter((item) => item.id_tarea_habilidad !== id));
    } catch (err) {
      setErrorHab(
        err instanceof Error ? err.message : "No se pudo quitar la habilidad",
      );
    }
  };

  const guardarTarea = async (id: number, cambios: Partial<Tarea>) => {
    const actualizada = await apiHab<Tarea>(`/tareas/${id}`, {
      method: "PUT",
      body: JSON.stringify(cambios),
    });
    setTareas((prev) =>
      prev.map((t) =>
        t.id_tarea === actualizada.id_tarea ? { ...t, ...actualizada } : t,
      ),
    );
    setSeleccionada((actual) =>
      actual && actual.id_tarea === actualizada.id_tarea
        ? { ...actual, ...actualizada }
        : actual,
    );
    return actualizada;
  };

  const cancelarTarea = async () => {
    if (!seleccionada) return;
    setErrorHab("");
    try {
      await guardarTarea(seleccionada.id_tarea, { estado: "CANCELADA" });
    } catch (err) {
      setErrorHab(err instanceof Error ? err.message : "No se pudo cancelar");
    }
  };

  const eliminarTarea = async () => {
    if (!seleccionada) return;
    setErrorHab("");
    try {
      await apiHab(`/tareas/${seleccionada.id_tarea}`, { method: "DELETE" });
      setTareas((prev) =>
        prev.filter((t) => t.id_tarea !== seleccionada.id_tarea),
      );
      setSeleccionada(null);
    } catch (err) {
      setErrorHab(
        err instanceof Error
          ? err.message
          : "No se pudo eliminar. Si ya tiene personas asignadas, cancélala.",
      );
    }
  };

  const cerrarForm = () => {
    if (guardando) return;
    setMostrarForm(false);
    setEditId(null);
  };

  const manejarSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setErrorForm("");
    setGuardando(true);

    try {
      if (!form.id_proyecto || !form.id_equipo) {
        throw new Error("Selecciona proyecto y equipo.");
      }
      if (form.fecha_limite < form.fecha_inicio) {
        throw new Error(
          "La fecha límite no puede ser anterior a la de inicio.",
        );
      }

      const payload: TareaCreate = {
        id_proyecto: Number(form.id_proyecto),
        id_equipo: Number(form.id_equipo),
        nombre: form.nombre.trim(),
        descripcion: form.descripcion?.trim() || null,
        prioridad: (form.prioridad || "MEDIA").toUpperCase(),
        horas_estimadas: Number(form.horas_estimadas),
        fecha_inicio: form.fecha_inicio,
        fecha_limite: form.fecha_limite,
      };

      if (editId) {
        await guardarTarea(editId, payload);
        setMostrarForm(false);
        setEditId(null);
      } else {
        const nueva = await crearTarea(payload);
        setTareas((prev) => [nueva, ...prev]);
        setProyectoFiltro(nueva.id_proyecto);
        setMostrarForm(false);
        setForm(formVacio);
        setSeleccionada(nueva);
      }
    } catch (err) {
      setErrorForm(
        err instanceof Error ? err.message : "No se pudo guardar la tarea",
      );
    } finally {
      setGuardando(false);
    }
  };

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
          <span className="tar-eyebrow">Trabajo</span>
          <h2>Tareas</h2>
          <p>
            {puedeCrear
              ? "El admin y la secretaria crean, corrigen o cancelan tareas."
              : "Elige un proyecto para ver sus tareas."}
          </p>
        </div>
        <div className="tar-hero-actions">
          <div className="tar-hero-stat">
            <strong>{tareasFiltradas.length}</strong>
            <span>
              {proyectoFiltro === "TODOS" ? "total" : "de este proyecto"}
            </span>
          </div>
          {puedeCrear && (
            <button
              type="button"
              className="tar-btn-primary"
              onClick={abrirForm}
            >
              + Nueva tarea
            </button>
          )}
        </div>
      </div>

      <div className="tar-toolbar">
        <label className="tar-proyecto">
          Proyecto
          <select
            value={
              proyectoFiltro === "TODOS" ? "TODOS" : String(proyectoFiltro)
            }
            onChange={(e) =>
              setProyectoFiltro(
                e.target.value === "TODOS" ? "TODOS" : Number(e.target.value),
              )
            }
          >
            <option value="TODOS">Todos los proyectos</option>
            {proyectos.map((proyecto) => (
              <option key={proyecto.id_proyecto} value={proyecto.id_proyecto}>
                {proyecto.nombre}
              </option>
            ))}
          </select>
        </label>

        <div className="tar-filters">
          {[
            "TODAS",
            "PENDIENTE",
            "EN_PROGRESO",
            "FINALIZADA",
            "ASIGNADA",
            "CANCELADA",
          ].map((f) => (
            <button
              key={f}
              type="button"
              className={filtro === f ? "tar-filter active" : "tar-filter"}
              onClick={() => setFiltro(f)}
            >
              {f === "TODAS" ? "Todas" : f.replace("_", " ")}
            </button>
          ))}
        </div>
      </div>

      {tareasFiltradas.length === 0 ? (
        <p className="tar-msg">
          {proyectoFiltro === "TODOS"
            ? "No hay tareas con este filtro."
            : `No hay tareas en ${nombreProyecto(proyectoFiltro)}.`}
        </p>
      ) : (
        <div className="tar-grid">
          {tareasFiltradas.map((tarea) => (
            <article
              key={tarea.id_tarea}
              className="tar-card"
              onClick={() => setSeleccionada(tarea)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  setSeleccionada(tarea);
                }
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
              <button
                type="button"
                className="tar-filter"
                onClick={(e) => {
                  e.stopPropagation();
                  setProyectoFiltro(tarea.id_proyecto);
                }}
              >
                {nombreProyecto(tarea.id_proyecto)}
              </button>
              <p className="tar-desc">
                {tarea.descripcion || "Sin descripción."}
              </p>
              <div className="tar-card-meta">
                <span
                  className={`tar-estado ${(tarea.estado || "").toLowerCase()}`}
                >
                  {tarea.estado}
                </span>
                <span>{nombreEquipo(tarea.id_equipo)}</span>
                <span>{soloFecha(tarea.fecha_limite)}</span>
                <span>{tarea.horas_estimadas} h</span>
              </div>
            </article>
          ))}
        </div>
      )}

      {seleccionada && !mostrarForm && (
        <div
          onClick={() => setSeleccionada(null)}
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 3000,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 20,
            background: "rgba(15, 23, 42, 0.45)",
          }}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
            style={{
              width: "min(560px, 100%)",
              maxHeight: "calc(100vh - 40px)",
              overflowY: "auto",
              padding: 20,
              background: "#fff",
              borderRadius: 16,
              boxShadow: "0 24px 64px rgba(15, 23, 42, 0.2)",
            }}
          >
            <div className="tar-modal-head">
              <div>
                <span className="tar-eyebrow">Detalle</span>
                <h3>{seleccionada.nombre}</h3>
              </div>
              <button type="button" onClick={() => setSeleccionada(null)}>
                ✕
              </button>
            </div>
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
                <strong>{soloFecha(seleccionada.fecha_inicio)}</strong>
              </div>
              <div>
                <span>Límite</span>
                <strong>{soloFecha(seleccionada.fecha_limite)}</strong>
              </div>
              <div>
                <span>ID</span>
                <strong>#{seleccionada.id_tarea}</strong>
              </div>
            </div>

            {puedeCrear && (
              <div className="tar-form-actions">
                <button
                  type="button"
                  className="tar-btn-primary"
                  onClick={abrirEdicion}
                >
                  Editar
                </button>
                <button
                  type="button"
                  className="tar-btn-secondary"
                  onClick={cancelarTarea}
                >
                  Cancelar tarea
                </button>
                <button
                  type="button"
                  className="tar-btn-secondary"
                  onClick={eliminarTarea}
                >
                  Eliminar
                </button>
              </div>
            )}

            <div className="tar-skills">
              <h4>Habilidades que exige OPTIMA</h4>
              {reqs.length === 0 ? (
                <p className="tar-desc">
                  Esta tarea todavía no pide habilidades.
                </p>
              ) : (
                <ul className="tar-skill-list">
                  {reqs.map((req) => (
                    <li key={req.id_tarea_habilidad}>
                      <span>
                        {nombreHab(req.id_habilidad)} ·{" "}
                        {nombreNivel(req.id_nivel)}
                      </span>
                      {puedeCrear && (
                        <button
                          type="button"
                          onClick={() =>
                            quitarHabilidad(req.id_tarea_habilidad)
                          }
                        >
                          Quitar
                        </button>
                      )}
                    </li>
                  ))}
                </ul>
              )}

              {puedeCrear && (
                <div className="tar-skill-form">
                  <select
                    value={idHab}
                    onChange={(e) => setIdHab(e.target.value)}
                  >
                    <option value="">Habilidad</option>
                    {habilidades.map((h) => (
                      <option key={h.id_habilidad} value={h.id_habilidad}>
                        {h.nombre}
                      </option>
                    ))}
                  </select>
                  <select
                    value={idNivel}
                    onChange={(e) => setIdNivel(e.target.value)}
                  >
                    <option value="">Nivel mínimo</option>
                    {niveles.map((n) => (
                      <option key={n.id_nivel} value={n.id_nivel}>
                        {n.nombre}
                      </option>
                    ))}
                  </select>
                  <button
                    type="button"
                    className="tar-btn-primary"
                    disabled={guardandoHab || !idHab || !idNivel}
                    onClick={agregarHabilidad}
                  >
                    {guardandoHab ? "..." : "Agregar"}
                  </button>
                </div>
              )}
              {errorHab && <p className="tar-form-error">{errorHab}</p>}
            </div>
          </div>
        </div>
      )}

      {mostrarForm && puedeCrear && (
        <div
          onClick={cerrarForm}
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 3000,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 20,
            background: "rgba(15, 23, 42, 0.45)",
          }}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
            className="tar-modal"
            style={{
              width: "min(520px, 100%)",
              maxHeight: "calc(100vh - 40px)",
              overflowY: "auto",
              padding: 20,
              background: "#fff",
              borderRadius: 16,
            }}
          >
            <div className="tar-modal-head">
              <div>
                <span className="tar-eyebrow">
                  {editId ? "Editar" : "Nueva"}
                </span>
                <h3>{editId ? "Corregir tarea" : "Crear tarea"}</h3>
              </div>
              <button type="button" onClick={cerrarForm} disabled={guardando}>
                ✕
              </button>
            </div>

            <form onSubmit={manejarSubmit} className="tar-form">
              <label>
                Proyecto
                <select
                  required
                  value={form.id_proyecto || ""}
                  onChange={(e) =>
                    setForm((f) => ({
                      ...f,
                      id_proyecto: Number(e.target.value),
                      id_equipo: 0,
                    }))
                  }
                >
                  <option value="">Selecciona...</option>
                  {proyectos.map((p) => (
                    <option key={p.id_proyecto} value={p.id_proyecto}>
                      {p.nombre}
                    </option>
                  ))}
                </select>
              </label>

              <label>
                Equipo
                <select
                  required
                  value={form.id_equipo || ""}
                  onChange={(e) =>
                    setForm((f) => ({
                      ...f,
                      id_equipo: Number(e.target.value),
                    }))
                  }
                  disabled={!form.id_proyecto}
                >
                  <option value="">
                    {!form.id_proyecto
                      ? "Elige proyecto primero"
                      : equiposDelProyecto.length === 0
                        ? "Sin equipos en este proyecto"
                        : "Selecciona..."}
                  </option>
                  {equiposDelProyecto.map((eq) => (
                    <option key={eq.id_equipo} value={eq.id_equipo}>
                      {eq.nombre}
                    </option>
                  ))}
                </select>
              </label>

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
                Descripción
                <textarea
                  rows={3}
                  value={form.descripcion ?? ""}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, descripcion: e.target.value }))
                  }
                />
              </label>

              <label>
                Prioridad
                <select
                  value={form.prioridad || "MEDIA"}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, prioridad: e.target.value }))
                  }
                >
                  <option value="BAJA">BAJA</option>
                  <option value="MEDIA">MEDIA</option>
                  <option value="ALTA">ALTA</option>
                  <option value="CRITICA">CRITICA</option>
                </select>
              </label>

              <label>
                Horas estimadas
                <input
                  type="number"
                  min={0.5}
                  step={0.5}
                  required
                  value={form.horas_estimadas}
                  onChange={(e) =>
                    setForm((f) => ({
                      ...f,
                      horas_estimadas: Number(e.target.value),
                    }))
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

              {errorForm && <p className="tar-form-error">{errorForm}</p>}

              <div className="tar-form-actions">
                <button
                  type="button"
                  className="tar-btn-secondary"
                  onClick={cerrarForm}
                  disabled={guardando}
                >
                  Cerrar
                </button>
                <button
                  type="submit"
                  className="tar-btn-primary"
                  disabled={guardando}
                >
                  {guardando
                    ? "Guardando..."
                    : editId
                      ? "Guardar cambios"
                      : "Crear tarea"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </section>
  );
}

export default Tareas;
