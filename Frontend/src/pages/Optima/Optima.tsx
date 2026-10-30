import { useEffect, useState } from "react";

import {
  obtenerTareas,
  obtenerProyectos,
  obtenerEquipos,
  obtenerPersonas,
} from "../../service/api";

import type { Tarea } from "../../types/tarea";
import type { Proyecto } from "../../types/proyecto";
import type { Equipo } from "../../types/equipo";
import type { Persona } from "../../types/persona";
import type { CandidatoOptima } from "../../types/optima";

import "./Optima.css";

type Modo = "tarea" | "equipo" | "lider";

type PersonaPropuesta = {
  id_persona: number;
  persona: string;
  puntuacion_liderazgo?: number | null;
  puntuacion_equipo?: number | null;
  explicacion?: string | null;
  contribucion?: string | null;
};

type PropuestaEquipo = {
  id_proyecto: number;
  proyecto: string;
  cobertura: number;
  lider: PersonaPropuesta | null;
  integrantes: PersonaPropuesta[];
  explicacion: string;
};

type PersonaGrupo = {
  id_persona: number;
  nombre: string;
};

type MiembroEquipo = {
  id_equipo_persona: number;
  id_equipo: number;
  id_persona: number;
  rol_equipo: string;
  dedicacion: number;
  fecha_fin?: string | null;
};

const API = "http://127.0.0.1:8000";

function hoy(): string {
  return new Date().toISOString().slice(0, 10);
}

function soloFecha(valor?: string | null): string {
  if (!valor) return hoy();
  return valor.slice(0, 10);
}

function nombrePersona(persona: Persona): string {
  return `${persona.nombre} ${persona.apellido}`.trim();
}

async function api<T>(ruta: string, opciones?: RequestInit): Promise<T> {
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
      : detalle || "No se pudo completar la acción";
    throw new Error(mensaje);
  }

  return respuesta.json();
}

function ordenar(lista: CandidatoOptima[]): CandidatoOptima[] {
  return [...lista].sort((a, b) => {
    if (a.elegible && !b.elegible) return -1;
    if (!a.elegible && b.elegible) return 1;
    if (a.ranking && b.ranking) return a.ranking - b.ranking;
    return (b.puntuacion_optima ?? 0) - (a.puntuacion_optima ?? 0);
  });
}

function Selector({
  label,
  value,
  placeholder,
  opciones,
  onChange,
  ancho,
}: {
  label: string;
  value: string;
  placeholder: string;
  opciones: { value: string; label: string }[];
  onChange: (value: string) => void;
  ancho?: boolean;
}) {
  const [abierto, setAbierto] = useState(false);
  const actual = opciones.find((opcion) => opcion.value === value);

  return (
    <div className={ancho ? "optima-field optima-field-wide" : "optima-field"}>
      <span>{label}</span>
      <div className="optima-select-wrapper">
        <button
          type="button"
          className="optima-select-btn"
          onClick={() => setAbierto((estado) => !estado)}
        >
          <span>{actual?.label || placeholder}</span>
          <span className="optima-select-arrow">{abierto ? "⌃" : "⌄"}</span>
        </button>
        {abierto && (
          <ul className="optima-menu">
            {opciones.length === 0 ? (
              <li>
                <button type="button" disabled>
                  Sin opciones
                </button>
              </li>
            ) : (
              opciones.map((opcion) => (
                <li key={opcion.value}>
                  <button
                    type="button"
                    className={opcion.value === value ? "active" : ""}
                    onClick={() => {
                      onChange(opcion.value);
                      setAbierto(false);
                    }}
                  >
                    {opcion.label}
                  </button>
                </li>
              ))
            )}
          </ul>
        )}
      </div>
    </div>
  );
}

function Optima() {
  const [modo, setModo] = useState<Modo>("tarea");
  const [proyectos, setProyectos] = useState<Proyecto[]>([]);
  const [tareas, setTareas] = useState<Tarea[]>([]);
  const [equipos, setEquipos] = useState<Equipo[]>([]);
  const [personas, setPersonas] = useState<Persona[]>([]);

  const [proyectoTarea, setProyectoTarea] = useState<number | null>(null);
  const [tareaId, setTareaId] = useState<number | null>(null);
  const [candidatos, setCandidatos] = useState<CandidatoOptima[]>([]);
  const [asignando, setAsignando] = useState<number | null>(null);
  const [asignados, setAsignados] = useState<number[]>([]);

  const [proyectoGrupo, setProyectoGrupo] = useState<number | null>(null);
  const [propuesta, setPropuesta] = useState<PropuestaEquipo | null>(null);
  const [grupo, setGrupo] = useState<PersonaGrupo[]>([]);
  const [personaExtra, setPersonaExtra] = useState("");
  const [equipoGrupo, setEquipoGrupo] = useState<number | null>(null);
  const [cerrandoGrupo, setCerrandoGrupo] = useState(false);
  const [resumenGrupo, setResumenGrupo] = useState("");

  const [proyectoLider, setProyectoLider] = useState<number | null>(null);
  const [equipoLider, setEquipoLider] = useState<number | null>(null);
  const [miembros, setMiembros] = useState<MiembroEquipo[]>([]);
  const [sugeridoId, setSugeridoId] = useState<number | null>(null);
  const [sugeridoNombre, setSugeridoNombre] = useState("");
  const [liderId, setLiderId] = useState<number | null>(null);
  const [guardandoLider, setGuardandoLider] = useState(false);

  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");
  const [aviso, setAviso] = useState("");

  useEffect(() => {
    Promise.all([
      obtenerProyectos(),
      obtenerTareas(),
      obtenerEquipos(),
      obtenerPersonas(),
    ])
      .then(([proyectosData, tareasData, equiposData, personasData]) => {
        setProyectos(proyectosData);
        setTareas(tareasData);
        setEquipos(equiposData);
        setPersonas(personasData);
      })
      .catch((err) =>
        setError(
          err instanceof Error ? err.message : "No se pudo cargar OPTIMA",
        ),
      );
  }, []);

  const tareasDelProyecto = tareas.filter(
    (tarea) => tarea.id_proyecto === proyectoTarea,
  );
  const tareaActual =
    tareas.find((tarea) => tarea.id_tarea === tareaId) || null;
  const equipoDeLaTarea = equipos.find(
    (equipo) => equipo.id_equipo === tareaActual?.id_equipo,
  );
  const equiposDelGrupo = equipos.filter(
    (equipo) => equipo.id_proyecto === proyectoGrupo,
  );
  const equiposDelLider = equipos.filter(
    (equipo) => equipo.id_proyecto === proyectoLider,
  );

  const evaluarTarea = async (idTarea: number) => {
    try {
      setCargando(true);
      setError("");
      setTareaId(idTarea);
      const data = await api<CandidatoOptima[]>(
        `/optima/tarea/${idTarea}?alcance=organizacion`,
      );
      setCandidatos(ordenar(data));

      const tarea = tareas.find((item) => item.id_tarea === idTarea);
      if (!tarea?.id_equipo) {
        setAsignados([]);
      } else {
        const [asignaciones, miembrosEq] = await Promise.all([
          api<{ id_equipo_persona: number }[]>(
            `/asignaciones-tareas/tarea/${idTarea}`,
          ),
          api<MiembroEquipo[]>(`/equipos-personas/equipo/${tarea.id_equipo}`),
        ]);
        const ids = new Set(asignaciones.map((item) => item.id_equipo_persona));
        setAsignados(
          miembrosEq
            .filter((miembro) => ids.has(miembro.id_equipo_persona))
            .map((miembro) => miembro.id_persona),
        );
      }
    } catch (err) {
      setCandidatos([]);
      setAsignados([]);
      setError(
        err instanceof Error ? err.message : "No se pudo analizar la tarea",
      );
    } finally {
      setCargando(false);
    }
  };

  const cargarPropuesta = async (idProyecto: number) => {
    try {
      setCargando(true);
      setError("");
      setAviso("");
      setResumenGrupo("");
      setProyectoGrupo(idProyecto);
      setEquipoGrupo(null);
      setGrupo([]);
      const data = await api<PropuestaEquipo>(
        `/optima/proyecto/${idProyecto}/propuesta-equipo`,
      );
      setPropuesta(data);
    } catch (err) {
      setPropuesta(null);
      setError(
        err instanceof Error ? err.message : "No se pudo armar la sugerencia",
      );
    } finally {
      setCargando(false);
    }
  };

  const usarSugerencia = () => {
    if (!propuesta) return;
    const vistos = new Set<number>();
    const lista: PersonaGrupo[] = [];
    propuesta.integrantes.forEach((persona) => {
      if (vistos.has(persona.id_persona)) return;
      vistos.add(persona.id_persona);
      lista.push({ id_persona: persona.id_persona, nombre: persona.persona });
    });
    setGrupo(lista);
    setAviso(
      "Sugerencia copiada al grupo final. Puedes quitar o agregar personas.",
    );
  };

  const agregarAlGrupo = () => {
    const id = Number(personaExtra);
    if (!id || grupo.some((persona) => persona.id_persona === id)) return;
    const persona = personas.find((item) => item.id_persona === id);
    if (!persona) return;
    setGrupo((actual) => [
      ...actual,
      { id_persona: id, nombre: nombrePersona(persona) },
    ]);
    setPersonaExtra("");
  };

  const asegurarEnEquipo = async (idEquipo: number, idPersona: number) => {
    const miembrosActuales = await api<MiembroEquipo[]>(
      `/equipos-personas/equipo/${idEquipo}`,
    );
    const activo = miembrosActuales.find(
      (miembro) => miembro.id_persona === idPersona && !miembro.fecha_fin,
    );
    if (activo) return activo.id_equipo_persona;

    const creado = await api<MiembroEquipo>("/equipos-personas/", {
      method: "POST",
      body: JSON.stringify({
        id_equipo: idEquipo,
        id_persona: idPersona,
        rol_equipo: "INTEGRANTE",
        dedicacion: 40,
        fecha_inicio: hoy(),
      }),
    });
    return creado.id_equipo_persona;
  };

  const asignarPersonaATarea = async (candidato: CandidatoOptima) => {
    if (!tareaActual || !equipoDeLaTarea) return;
    try {
      setAsignando(candidato.id_persona);
      setError("");
      setAviso("");
      const idEquipoPersona = await asegurarEnEquipo(
        equipoDeLaTarea.id_equipo,
        candidato.id_persona,
      );
      await api("/asignaciones-tareas/", {
        method: "POST",
        body: JSON.stringify({
          id_tarea: tareaActual.id_tarea,
          id_equipo_persona: idEquipoPersona,
          fecha_asignacion: hoy(),
          fecha_inicio: soloFecha(tareaActual.fecha_inicio),
          fecha_limite: soloFecha(tareaActual.fecha_limite),
          dedicacion: 40,
        }),
      });
      setAsignados((actual) =>
        actual.includes(candidato.id_persona)
          ? actual
          : [...actual, candidato.id_persona],
      );
      setAviso(
        `${candidato.persona} quedó asignado en ${equipoDeLaTarea.nombre}.`,
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo asignar");
    } finally {
      setAsignando(null);
    }
  };

  const cerrarGrupo = async () => {
    if (!equipoGrupo || grupo.length === 0) return;
    try {
      setCerrandoGrupo(true);
      setError("");
      setResumenGrupo("");
      const idsGrupo = new Set(grupo.map((persona) => persona.id_persona));

      for (const persona of grupo) {
        await asegurarEnEquipo(equipoGrupo, persona.id_persona);
      }

      const miembrosActuales = await api<MiembroEquipo[]>(
        `/equipos-personas/equipo/${equipoGrupo}`,
      );
      const porPersona = new Map<number, number>();
      miembrosActuales
        .filter((miembro) => !miembro.fecha_fin)
        .forEach((miembro) =>
          porPersona.set(miembro.id_persona, miembro.id_equipo_persona),
        );

      const tareasDelEquipo = tareas.filter(
        (tarea) =>
          tarea.id_equipo === equipoGrupo &&
          ["PENDIENTE", "EN_PROGRESO"].includes(
            (tarea.estado || "").toUpperCase(),
          ),
      );

      const hechas: string[] = [];
      const saltadas: string[] = [];

      for (const tarea of tareasDelEquipo) {
        try {
          const ranking = ordenar(
            await api<CandidatoOptima[]>(
              `/optima/tarea/${tarea.id_tarea}?alcance=organizacion`,
            ),
          );
          const mejor = ranking.find(
            (candidato) =>
              candidato.elegible && idsGrupo.has(candidato.id_persona),
          );
          if (!mejor) {
            saltadas.push(`${tarea.nombre}: nadie del grupo es elegible`);
            continue;
          }
          const idEquipoPersona = porPersona.get(mejor.id_persona);
          if (!idEquipoPersona) {
            saltadas.push(`${tarea.nombre}: la persona no quedó en el equipo`);
            continue;
          }
          await api("/asignaciones-tareas/", {
            method: "POST",
            body: JSON.stringify({
              id_tarea: tarea.id_tarea,
              id_equipo_persona: idEquipoPersona,
              fecha_asignacion: hoy(),
              fecha_inicio: soloFecha(tarea.fecha_inicio),
              fecha_limite: soloFecha(tarea.fecha_limite),
              dedicacion: 40,
            }),
          });
          hechas.push(`${tarea.nombre} → ${mejor.persona}`);
        } catch (err) {
          const mensaje = err instanceof Error ? err.message : "No se asignó";
          if (mensaje.toLowerCase().includes("ya está asignada")) {
            hechas.push(`${tarea.nombre}: ya estaba asignada`);
          } else {
            saltadas.push(`${tarea.nombre}: ${mensaje}`);
          }
        }
      }

      setResumenGrupo(
        [
          `Grupo listo. ${hechas.length} asignación(es).`,
          ...hechas.map((linea) => `• ${linea}`),
          saltadas.length ? "Sin asignar:" : "",
          ...saltadas.map((linea) => `• ${linea}`),
        ]
          .filter(Boolean)
          .join("\n"),
      );
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "No se pudo cerrar el grupo",
      );
    } finally {
      setCerrandoGrupo(false);
    }
  };

  const cargarLider = async (idEquipo: number, idProyecto: number) => {
    try {
      setCargando(true);
      setError("");
      setAviso("");
      setEquipoLider(idEquipo);
      const [miembrosData, propuestaData] = await Promise.all([
        api<MiembroEquipo[]>(`/equipos-personas/equipo/${idEquipo}`),
        api<PropuestaEquipo>(`/optima/proyecto/${idProyecto}/propuesta-equipo`),
      ]);
      const activos = miembrosData.filter((miembro) => !miembro.fecha_fin);
      setMiembros(activos);
      const ids = new Set(activos.map((miembro) => miembro.id_persona));
      if (propuestaData.lider && ids.has(propuestaData.lider.id_persona)) {
        setSugeridoId(propuestaData.lider.id_persona);
        setSugeridoNombre(propuestaData.lider.persona);
        setLiderId(propuestaData.lider.id_persona);
      } else {
        setSugeridoId(null);
        setSugeridoNombre(propuestaData.lider?.persona || "");
        setLiderId(activos[0]?.id_persona ?? null);
      }
    } catch (err) {
      setMiembros([]);
      setError(
        err instanceof Error ? err.message : "No se pudo sugerir el líder",
      );
    } finally {
      setCargando(false);
    }
  };

  const aceptarLider = async () => {
    if (!liderId) return;
    const elegido = miembros.find((miembro) => miembro.id_persona === liderId);
    if (!elegido) return;
    try {
      setGuardandoLider(true);
      setError("");
      await api(`/equipos-personas/${elegido.id_equipo_persona}`, {
        method: "PUT",
        body: JSON.stringify({ rol_equipo: "LIDER" }),
      });
      const otros = miembros.filter(
        (miembro) =>
          miembro.id_persona !== liderId &&
          miembro.rol_equipo.toUpperCase().includes("LIDER"),
      );
      for (const miembro of otros) {
        await api(`/equipos-personas/${miembro.id_equipo_persona}`, {
          method: "PUT",
          body: JSON.stringify({ rol_equipo: "INTEGRANTE" }),
        });
      }
      setAviso(
        "Líder aceptado. El admin decidió y quedó guardado en el equipo.",
      );
      if (equipoLider && proyectoLider) {
        await cargarLider(equipoLider, proyectoLider);
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "No se pudo guardar el líder",
      );
    } finally {
      setGuardandoLider(false);
    }
  };

  const nombreDe = (idPersona: number) => {
    const persona = personas.find((item) => item.id_persona === idPersona);
    return persona ? nombrePersona(persona) : `Persona #${idPersona}`;
  };

  return (
    <section className="optima-page">
      <div className="optima-hero">
        <div className="optima-hero-content">
          <div className="optima-engine-label">
            <span className="optima-engine-dot" />
            OPTIMA ENGINE
          </div>
          <h2>
            Optimización <span>inteligente</span>
          </h2>
          <p>
            OPTIMA sugiere. El admin crea el equipo, confirma el grupo y acepta
            al líder.
          </p>
        </div>
        <div className="optima-hero-symbol">
          <span>✦</span>
        </div>
      </div>

      <div className="optima-tabs">
        <button
          type="button"
          className={modo === "tarea" ? "optima-tab active" : "optima-tab"}
          onClick={() => setModo("tarea")}
        >
          Por tarea
        </button>
        <button
          type="button"
          className={modo === "equipo" ? "optima-tab active" : "optima-tab"}
          onClick={() => setModo("equipo")}
        >
          OPTIMA Team
        </button>
        <button
          type="button"
          className={modo === "lider" ? "optima-tab active" : "optima-tab"}
          onClick={() => setModo("lider")}
        >
          Líder
        </button>
      </div>

      {error && <p className="optima-error">{error}</p>}
      {aviso && <p className="optima-alcance-note">{aviso}</p>}

      {modo === "tarea" && (
        <div className="optima-control">
          <div className="optima-control-title">
            <div className="optima-control-icon">⌁</div>
            <div>
              <span>ANÁLISIS DE TAREA</span>
              <h3>Proyecto, tarea y ranking de la organización</h3>
            </div>
          </div>
          <Selector
            label="Proyecto"
            value={proyectoTarea ? String(proyectoTarea) : ""}
            placeholder="Selecciona un proyecto"
            ancho
            opciones={proyectos.map((proyecto) => ({
              value: String(proyecto.id_proyecto),
              label: proyecto.nombre,
            }))}
            onChange={(valor) => {
              setProyectoTarea(valor ? Number(valor) : null);
              setTareaId(null);
              setCandidatos([]);
              setAsignados([]);
            }}
          />
          <Selector
            label="Tarea"
            value={tareaId ? String(tareaId) : ""}
            placeholder="Tareas de ese proyecto"
            ancho
            opciones={tareasDelProyecto.map((tarea) => ({
              value: String(tarea.id_tarea),
              label: tarea.nombre,
            }))}
            onChange={(valor) => {
              if (!valor) {
                setTareaId(null);
                setCandidatos([]);
                setAsignados([]);
                return;
              }
              evaluarTarea(Number(valor));
            }}
          />
          {tareaActual && (
            <p className="optima-alcance-note">
              {equipoDeLaTarea
                ? `Esta tarea pertenece a ${equipoDeLaTarea.nombre}. Al asignar, la persona entra a ese equipo y recibe solo esta tarea.`
                : "Esta tarea no tiene un equipo activo. Créalo en Equipos antes de asignar."}
            </p>
          )}
        </div>
      )}

      {modo === "equipo" && (
        <div className="optima-control">
          <div className="optima-control-title">
            <div className="optima-control-icon">✦</div>
            <div>
              <span>SUGERENCIA</span>
              <h3>OPTIMA propone. Tú armas el grupo final.</h3>
            </div>
          </div>
          <Selector
            label="Proyecto"
            value={proyectoGrupo ? String(proyectoGrupo) : ""}
            placeholder="Selecciona un proyecto"
            ancho
            opciones={proyectos.map((proyecto) => ({
              value: String(proyecto.id_proyecto),
              label: proyecto.nombre,
            }))}
            onChange={(valor) => {
              if (!valor) {
                setProyectoGrupo(null);
                setPropuesta(null);
                return;
              }
              cargarPropuesta(Number(valor));
            }}
          />
          <p className="optima-alcance-note">
            Si la sugerencia te sirve, úsala. Si no, quita o agrega personas. El
            equipo se crea en Equipos. Grupo listo mete al grupo en ese equipo y
            reparte las tareas de ese equipo.
          </p>
        </div>
      )}

      {modo === "lider" && (
        <div className="optima-control">
          <div className="optima-control-title">
            <div className="optima-control-icon">★</div>
            <div>
              <span>LÍDER</span>
              <h3>Cuando el grupo ya está en el equipo</h3>
            </div>
          </div>
          <Selector
            label="Proyecto"
            value={proyectoLider ? String(proyectoLider) : ""}
            placeholder="Selecciona un proyecto"
            opciones={proyectos.map((proyecto) => ({
              value: String(proyecto.id_proyecto),
              label: proyecto.nombre,
            }))}
            onChange={(valor) => {
              setProyectoLider(valor ? Number(valor) : null);
              setEquipoLider(null);
              setMiembros([]);
            }}
          />
          <Selector
            label="Equipo"
            value={equipoLider ? String(equipoLider) : ""}
            placeholder="Equipo ya creado"
            opciones={equiposDelLider.map((equipo) => ({
              value: String(equipo.id_equipo),
              label: equipo.nombre,
            }))}
            onChange={(valor) => {
              if (!valor || !proyectoLider) return;
              cargarLider(Number(valor), proyectoLider);
            }}
          />
        </div>
      )}

      {cargando && (
        <div className="optima-loading">
          <strong>OPTIMA está calculando</strong>
          <p>Revisando habilidades, carga y disponibilidad.</p>
        </div>
      )}

      {modo === "tarea" && !cargando && candidatos.length > 0 && (
        <div className="optima-results">
          <div className="optima-results-heading">
            <div>
              <span className="optima-label">RANKING DE LA ORGANIZACIÓN</span>
              <h3>{tareaActual?.nombre}</h3>
            </div>
            <div className="optima-results-count">
              {candidatos.filter((candidato) => candidato.elegible).length}{" "}
              elegibles
            </div>
          </div>
          <div className="optima-grid">
            {candidatos.map((candidato) => (
              <article key={candidato.id_persona} className="optima-card">
                <div className="optima-card-top">
                  <div className="optima-person">
                    <div className="optima-person-avatar">
                      {candidato.persona.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <span className="optima-person-label">
                        {candidato.ranking
                          ? `#${candidato.ranking}`
                          : "Candidato"}
                      </span>
                      <h4>{candidato.persona}</h4>
                    </div>
                  </div>
                </div>
                <div className="optima-status-row">
                  <span
                    className={`optima-status ${
                      candidato.elegible
                        ? "optima-status-success"
                        : "optima-status-danger"
                    }`}
                  >
                    {candidato.elegible ? "Elegible" : "No elegible"}
                  </span>
                  <span className="optima-badge">
                    {candidato.puntuacion_optima?.toFixed(2) ?? "0.00"}
                  </span>
                </div>
                <div className="optima-capacity">
                  <div>
                    <span>COMPATIBILIDAD</span>
                    <strong>
                      {candidato.compatibilidad?.toFixed(0) ?? 0}%
                    </strong>
                  </div>
                  <div>
                    <span>DISPONIBILIDAD</span>
                    <strong>
                      {candidato.disponibilidad?.toFixed(0) ?? 0}%
                    </strong>
                  </div>
                </div>
                {candidato.explicacion && (
                  <p className="optima-explanation">{candidato.explicacion}</p>
                )}
                {asignados.includes(candidato.id_persona) ? (
                  <div className="optima-actions">
                    <span className="optima-status optima-status-success">
                      Asignado
                    </span>
                  </div>
                ) : (
                  candidato.elegible &&
                  equipoDeLaTarea && (
                    <div className="optima-actions">
                      <button
                        type="button"
                        className="optima-btn"
                        disabled={asignando === candidato.id_persona}
                        onClick={() => asignarPersonaATarea(candidato)}
                      >
                        {asignando === candidato.id_persona
                          ? "Asignando..."
                          : "Asignar a esta tarea"}
                      </button>
                    </div>
                  )
                )}
              </article>
            ))}
          </div>
        </div>
      )}

      {modo === "equipo" && propuesta && !cargando && (
        <div className="optima-results">
          <div className="optima-results-heading">
            <div>
              <span className="optima-label">LO QUE SUGIERE OPTIMA</span>
              <h3>{propuesta.proyecto}</h3>
            </div>
            <div className="optima-results-count">
              Cobertura {propuesta.cobertura.toFixed(0)}%
            </div>
          </div>
          <div className="optima-grid">
            {propuesta.integrantes.map((persona) => (
              <article key={persona.id_persona} className="optima-card">
                <div className="optima-person">
                  <div className="optima-person-avatar">
                    {persona.persona.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <span className="optima-person-label">Sugerido</span>
                    <h4>{persona.persona}</h4>
                  </div>
                </div>
                <p className="optima-explanation">
                  {persona.contribucion || persona.explicacion}
                </p>
              </article>
            ))}
          </div>
          <p className="optima-explanation">{propuesta.explicacion}</p>

          <div className="optima-actions">
            <button
              type="button"
              className="optima-btn"
              onClick={usarSugerencia}
            >
              Usar esta sugerencia
            </button>
          </div>

          <div className="optima-task-summary">
            <span className="optima-label">GRUPO FINAL</span>
            <h3>El admin decide quién se queda</h3>
            {grupo.length === 0 ? (
              <p>Todavía no hay grupo final.</p>
            ) : (
              <ul className="optima-final">
                {grupo.map((persona) => (
                  <li key={persona.id_persona}>
                    <strong>{persona.nombre}</strong>
                    <button
                      type="button"
                      className="optima-btn-ghost"
                      onClick={() =>
                        setGrupo((actual) =>
                          actual.filter(
                            (item) => item.id_persona !== persona.id_persona,
                          ),
                        )
                      }
                    >
                      Quitar
                    </button>
                  </li>
                ))}
              </ul>
            )}
            <div className="optima-actions">
              <Selector
                label="Agregar otra persona"
                value={personaExtra}
                placeholder="Alguien que OPTIMA no sugirió"
                ancho
                opciones={personas
                  .filter(
                    (persona) =>
                      !grupo.some(
                        (item) => item.id_persona === persona.id_persona,
                      ),
                  )
                  .map((persona) => ({
                    value: String(persona.id_persona),
                    label: nombrePersona(persona),
                  }))}
                onChange={setPersonaExtra}
              />
              <button
                type="button"
                className="optima-btn-ghost"
                onClick={agregarAlGrupo}
                disabled={!personaExtra}
              >
                Agregar al grupo
              </button>
            </div>
            <Selector
              label="Equipo que ya creaste"
              value={equipoGrupo ? String(equipoGrupo) : ""}
              placeholder={
                equiposDelGrupo.length
                  ? "Selecciona el equipo"
                  : "Este proyecto no tiene equipo"
              }
              ancho
              opciones={equiposDelGrupo.map((equipo) => ({
                value: String(equipo.id_equipo),
                label: equipo.nombre,
              }))}
              onChange={(valor) => setEquipoGrupo(valor ? Number(valor) : null)}
            />
            {!equiposDelGrupo.length && (
              <p>Primero crea el equipo en Equipos. OPTIMA no lo crea.</p>
            )}
            <div className="optima-actions">
              <button
                type="button"
                className="optima-btn"
                disabled={!equipoGrupo || grupo.length === 0 || cerrandoGrupo}
                onClick={cerrarGrupo}
              >
                {cerrandoGrupo ? "Asignando..." : "Grupo listo"}
              </button>
            </div>
            {resumenGrupo && (
              <p className="optima-explanation optima-resumen">
                {resumenGrupo}
              </p>
            )}
          </div>
        </div>
      )}

      {modo === "lider" && !cargando && equipoLider && (
        <div className="optima-results">
          <div className="optima-results-heading">
            <div>
              <span className="optima-label">LÍDER SUGERIDO</span>
              <h3>
                {sugeridoId
                  ? sugeridoNombre
                  : "OPTIMA no encontró a su líder dentro de este equipo"}
              </h3>
            </div>
          </div>
          {!sugeridoId && sugeridoNombre && (
            <p className="optima-alcance-note">
              OPTIMA sugiere a {sugeridoNombre}, pero no está en este equipo.
              Elige un líder entre los miembros actuales.
            </p>
          )}
          {miembros.length === 0 ? (
            <p className="optima-explanation">
              Este equipo todavía no tiene miembros.
            </p>
          ) : (
            <div className="optima-grid">
              {miembros.map((miembro) => (
                <article
                  key={miembro.id_equipo_persona}
                  className={
                    miembro.id_persona === liderId
                      ? "optima-card optima-card-recommended"
                      : "optima-card"
                  }
                >
                  <div className="optima-person">
                    <div className="optima-person-avatar">
                      {nombreDe(miembro.id_persona).charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <span className="optima-person-label">
                        {miembro.id_persona === sugeridoId
                          ? "Sugerido por OPTIMA"
                          : miembro.rol_equipo}
                      </span>
                      <h4>{nombreDe(miembro.id_persona)}</h4>
                    </div>
                  </div>
                  <div className="optima-actions">
                    <button
                      type="button"
                      className="optima-btn-ghost"
                      onClick={() => setLiderId(miembro.id_persona)}
                    >
                      {liderId === miembro.id_persona ? "Elegido" : "Elegir"}
                    </button>
                  </div>
                </article>
              ))}
            </div>
          )}
          <div className="optima-actions">
            <button
              type="button"
              className="optima-btn"
              disabled={!liderId || guardandoLider}
              onClick={aceptarLider}
            >
              {guardandoLider ? "Guardando..." : "Aceptar líder"}
            </button>
          </div>
        </div>
      )}
    </section>
  );
}

export default Optima;
