import { useEffect, useState } from "react";

import {
  obtenerProyectos,
  obtenerEquipos,
  obtenerTareas,
  obtenerPersonas,
} from "../../service/api";
import { useAuth } from "../../context/AuthContext";
import { ROLES } from "../../utils/roles";

import type { Proyecto } from "../../types/proyecto";
import type { Equipo } from "../../types/equipo";
import type { Tarea } from "../../types/tarea";
import type { Persona } from "../../types/persona";

import "./Equipos.css";

type TareaNueva = {
  nombre: string;
  prioridad: string;
  horas: string;
  inicio: string;
  limite: string;
};

type Miembro = {
  id_equipo_persona: number;
  id_persona: number;
  rol_equipo: string;
  dedicacion: number;
  fecha_fin?: string | null;
};

const API = "http://127.0.0.1:8000";

const filaVacia = (): TareaNueva => ({
  nombre: "",
  prioridad: "MEDIA",
  horas: "8",
  inicio: "",
  limite: "",
});

async function api<T>(ruta: string, opciones?: RequestInit): Promise<T> {
  const token = localStorage.getItem("flowos_token");
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
    throw new Error(
      typeof detalle === "string" ? detalle : "No se pudo guardar el equipo",
    );
  }
  return respuesta.json();
}

function Equipos() {
  const { usuario } = useAuth();
  const puedeCrear =
    usuario?.id_rol === ROLES.ADMIN ||
    usuario?.id_rol === ROLES.SECRETARIO ||
    usuario?.id_rol === ROLES.LIDER_PROYECTO;

  const [proyectos, setProyectos] = useState<Proyecto[]>([]);
  const [equipos, setEquipos] = useState<Equipo[]>([]);
  const [tareas, setTareas] = useState<Tarea[]>([]);
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [idProyecto, setIdProyecto] = useState<number | null>(null);
  const [elegido, setElegido] = useState<number | null>(null);
  const [miembros, setMiembros] = useState<Miembro[]>([]);
  const [abierto, setAbierto] = useState(false);
  const [nombre, setNombre] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [filas, setFilas] = useState<TareaNueva[]>([filaVacia()]);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState("");
  const [aviso, setAviso] = useState("");

  const cargar = async () => {
    const [proyectosData, equiposData, tareasData, personasData] =
      await Promise.all([
        obtenerProyectos(),
        obtenerEquipos(),
        obtenerTareas(),
        obtenerPersonas(),
      ]);
    setProyectos(proyectosData);
    setEquipos(equiposData);
    setTareas(tareasData);
    setPersonas(personasData);
    setIdProyecto((actual) => actual ?? proyectosData[0]?.id_proyecto ?? null);
  };

  useEffect(() => {
    cargar().catch((err) =>
      setError(
        err instanceof Error
          ? err.message
          : "No se pudieron cargar los equipos",
      ),
    );
  }, []);

  useEffect(() => {
    if (!elegido) {
      setMiembros([]);
      return;
    }
    api<Miembro[]>(`/equipos-personas/equipo/${elegido}`)
      .then((data) => setMiembros(data.filter((item) => !item.fecha_fin)))
      .catch(() => setMiembros([]));
  }, [elegido]);

  const proyectoActual =
    proyectos.find((proyecto) => proyecto.id_proyecto === idProyecto) || null;

  const equiposDelProyecto = equipos.filter(
    (equipo) => equipo.id_proyecto === idProyecto,
  );

  const nombrePersona = (id: number) => {
    const persona = personas.find((item) => item.id_persona === id);
    return persona ? `${persona.nombre} ${persona.apellido}` : `Persona #${id}`;
  };

  const abrirForm = () => {
    if (!idProyecto) return;
    setNombre("");
    setDescripcion("");
    setFilas([filaVacia()]);
    setError("");
    setAbierto(true);
  };

  const crear = async () => {
    if (!idProyecto || !nombre.trim()) return;
    const utiles = filas.filter(
      (fila) => fila.nombre.trim() && fila.inicio && fila.limite,
    );
    try {
      setGuardando(true);
      setError("");
      const equipo = await api<Equipo>("/equipos/", {
        method: "POST",
        body: JSON.stringify({
          id_proyecto: idProyecto,
          nombre: nombre.trim(),
          descripcion: descripcion.trim() || null,
        }),
      });
      for (const fila of utiles) {
        await api("/tareas/", {
          method: "POST",
          body: JSON.stringify({
            id_proyecto: idProyecto,
            id_equipo: equipo.id_equipo,
            nombre: fila.nombre.trim(),
            descripcion: null,
            prioridad: fila.prioridad,
            horas_estimadas: Number(fila.horas) || 8,
            fecha_inicio: fila.inicio,
            fecha_limite: fila.limite,
          }),
        });
      }
      await cargar();
      setElegido(equipo.id_equipo);
      setAbierto(false);
      setAviso(
        `Equipo "${equipo.nombre}" creado en ${proyectoActual?.nombre || "el proyecto"} con ${utiles.length} tarea(s).`,
      );
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "No se pudo crear el equipo",
      );
    } finally {
      setGuardando(false);
    }
  };

  const equipoActual =
    equiposDelProyecto.find((equipo) => equipo.id_equipo === elegido) || null;
  const tareasDelEquipo = tareas.filter((tarea) => tarea.id_equipo === elegido);

  return (
    <section className="eq-page">
      <header className="eq-head">
        <div>
          <span>EQUIPOS</span>
          <h1>Equipos del proyecto</h1>
          <p>Elige el proyecto y ahí creas sus equipos.</p>
        </div>
      </header>

      <div className="eq-toolbar">
        <label>
          Proyecto
          <select
            value={idProyecto ?? ""}
            onChange={(e) => {
              setIdProyecto(e.target.value ? Number(e.target.value) : null);
              setElegido(null);
              setAviso("");
            }}
          >
            <option value="">Selecciona un proyecto</option>
            {proyectos.map((proyecto) => (
              <option key={proyecto.id_proyecto} value={proyecto.id_proyecto}>
                {proyecto.nombre}
              </option>
            ))}
          </select>
        </label>
        {puedeCrear && (
          <button
            type="button"
            className="eq-btn"
            disabled={!idProyecto}
            onClick={abrirForm}
          >
            Crear equipo
          </button>
        )}
      </div>

      {error && <p className="eq-error">{error}</p>}
      {aviso && <p className="eq-ok">{aviso}</p>}

      {!idProyecto ? (
        <p className="eq-muted">
          Selecciona un proyecto para ver y crear equipos.
        </p>
      ) : equiposDelProyecto.length === 0 ? (
        <p className="eq-muted">
          {proyectoActual?.nombre} todavía no tiene equipos.
        </p>
      ) : (
        <div className="eq-grid">
          {equiposDelProyecto.map((equipo) => {
            const cantidad = tareas.filter(
              (tarea) => tarea.id_equipo === equipo.id_equipo,
            ).length;
            return (
              <button
                key={equipo.id_equipo}
                type="button"
                className={
                  elegido === equipo.id_equipo ? "eq-card active" : "eq-card"
                }
                onClick={() => setElegido(equipo.id_equipo)}
              >
                <span>{proyectoActual?.nombre}</span>
                <strong>{equipo.nombre}</strong>
                <small>
                  {cantidad} tarea(s) · {equipo.estado}
                </small>
              </button>
            );
          })}
        </div>
      )}

      {equipoActual && (
        <div className="eq-detail">
          <h2>{equipoActual.nombre}</h2>
          <p>{proyectoActual?.nombre}</p>
          <div className="eq-cols">
            <div>
              <h3>Tareas</h3>
              {tareasDelEquipo.length === 0 ? (
                <p className="eq-muted">Este equipo todavía no tiene tareas.</p>
              ) : (
                tareasDelEquipo.map((tarea) => (
                  <article key={tarea.id_tarea}>
                    <strong>{tarea.nombre}</strong>
                    <span>
                      {tarea.prioridad} · {tarea.horas_estimadas} h ·{" "}
                      {tarea.estado}
                    </span>
                  </article>
                ))
              )}
            </div>
            <div>
              <h3>Integrantes</h3>
              {miembros.length === 0 ? (
                <p className="eq-muted">Todavía no hay personas asignadas.</p>
              ) : (
                miembros.map((miembro) => (
                  <article key={miembro.id_equipo_persona}>
                    <strong>{nombrePersona(miembro.id_persona)}</strong>
                    <span>
                      {miembro.rol_equipo} · {miembro.dedicacion}%
                    </span>
                  </article>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {abierto && proyectoActual && (
        <div className="eq-modal">
          <form
            className="eq-form"
            onSubmit={(event) => {
              event.preventDefault();
              crear();
            }}
          >
            <div className="eq-form-head">
              <div>
                <span>NUEVO EQUIPO</span>
                <h2>{proyectoActual.nombre}</h2>
              </div>
              <button type="button" onClick={() => setAbierto(false)}>
                ×
              </button>
            </div>

            <label>
              Proyecto
              <input value={proyectoActual.nombre} readOnly />
            </label>
            <label>
              Nombre del equipo
              <input
                required
                value={nombre}
                placeholder="Ej. Equipo backend"
                onChange={(e) => setNombre(e.target.value)}
              />
            </label>
            <label>
              Descripción
              <input
                value={descripcion}
                placeholder="Opcional"
                onChange={(e) => setDescripcion(e.target.value)}
              />
            </label>

            <h3>Tareas de este equipo</h3>
            {filas.map((fila, indice) => (
              <div className="eq-row" key={indice}>
                <input
                  placeholder="Nombre de la tarea"
                  value={fila.nombre}
                  onChange={(e) =>
                    setFilas((actual) =>
                      actual.map((item, i) =>
                        i === indice
                          ? { ...item, nombre: e.target.value }
                          : item,
                      ),
                    )
                  }
                />
                <select
                  value={fila.prioridad}
                  onChange={(e) =>
                    setFilas((actual) =>
                      actual.map((item, i) =>
                        i === indice
                          ? { ...item, prioridad: e.target.value }
                          : item,
                      ),
                    )
                  }
                >
                  <option value="BAJA">Baja</option>
                  <option value="MEDIA">Media</option>
                  <option value="ALTA">Alta</option>
                  <option value="CRITICA">Crítica</option>
                </select>
                <input
                  type="number"
                  min={1}
                  value={fila.horas}
                  onChange={(e) =>
                    setFilas((actual) =>
                      actual.map((item, i) =>
                        i === indice
                          ? { ...item, horas: e.target.value }
                          : item,
                      ),
                    )
                  }
                />
                <input
                  type="date"
                  value={fila.inicio}
                  onChange={(e) =>
                    setFilas((actual) =>
                      actual.map((item, i) =>
                        i === indice
                          ? { ...item, inicio: e.target.value }
                          : item,
                      ),
                    )
                  }
                />
                <input
                  type="date"
                  value={fila.limite}
                  onChange={(e) =>
                    setFilas((actual) =>
                      actual.map((item, i) =>
                        i === indice
                          ? { ...item, limite: e.target.value }
                          : item,
                      ),
                    )
                  }
                />
              </div>
            ))}
            <button
              type="button"
              className="eq-btn-ghost"
              onClick={() => setFilas((actual) => [...actual, filaVacia()])}
            >
              Agregar otra tarea
            </button>
            <div className="eq-form-actions">
              <button
                type="button"
                className="eq-btn-ghost"
                onClick={() => setAbierto(false)}
              >
                Cancelar
              </button>
              <button type="submit" className="eq-btn" disabled={guardando}>
                {guardando ? "Creando..." : "Crear equipo"}
              </button>
            </div>
          </form>
        </div>
      )}
    </section>
  );
}

export default Equipos;
