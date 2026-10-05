import { useEffect, useState } from "react";

import {
  obtenerTareas,
  obtenerProyectos,
  evaluarTareaOptima,
  proponerEquipoOptima,
  confirmarPropuestaOptima,
  type AlcanceOptima,
} from "../../service/api";

import type { Tarea } from "../../types/tarea";
import type { Proyecto } from "../../types/proyecto";
import type { CandidatoOptima, PropuestaEquipo } from "../../types/optima";

import "./Optima.css";

type ModoOptima = "tarea" | "equipo";

function textoAlcance(alcance: AlcanceOptima): string {
  switch (alcance) {
    case "proyecto":
      return "personas en equipos de este proyecto";
    case "organizacion":
      return "personas activas de toda la organización";
    default:
      return "integrantes activos del equipo responsable de esta tarea";
  }
}

function Optima() {
  const [modo, setModo] = useState<ModoOptima>("tarea");

  const [tareas, setTareas] = useState<Tarea[]>([]);
  const [tareaSeleccionada, setTareaSeleccionada] = useState<number | null>(
    null,
  );
  const [candidatos, setCandidatos] = useState<CandidatoOptima[]>([]);
  const [alcance, setAlcance] = useState<AlcanceOptima>("equipo");

  const [proyectos, setProyectos] = useState<Proyecto[]>([]);
  const [proyectoSeleccionado, setProyectoSeleccionado] = useState<
    number | null
  >(null);
  const [propuesta, setPropuesta] = useState<PropuestaEquipo | null>(null);

  const [cargando, setCargando] = useState(false);

  const [confirmando, setConfirmando] = useState(false);
  const [msgConfirmacion, setMsgConfirmacion] = useState("");
  const [errConfirmacion, setErrConfirmacion] = useState("");

  useEffect(() => {
    obtenerTareas()
      .then(setTareas)
      .catch((error) => console.error("Error al obtener tareas:", error));

    obtenerProyectos()
      .then(setProyectos)
      .catch((error) => console.error("Error al obtener proyectos:", error));
  }, []);

  const evaluarTarea = async (
    idTarea: number,
    alcanceActual: AlcanceOptima = alcance,
  ) => {
    try {
      setCargando(true);
      setTareaSeleccionada(idTarea);

      const resultados = await evaluarTareaOptima(idTarea, alcanceActual);

      const resultadosOrdenados = [...resultados].sort((a, b) => {
        if (a.elegible && !b.elegible) return -1;
        if (!a.elegible && b.elegible) return 1;
        if (a.ranking && b.ranking) return a.ranking - b.ranking;
        return (b.puntuacion_optima ?? 0) - (a.puntuacion_optima ?? 0);
      });

      setCandidatos(resultadosOrdenados);
    } catch (error) {
      console.error("Error al ejecutar OPTIMA:", error);
      setCandidatos([]);
    } finally {
      setCargando(false);
    }
  };

  const analizarEquipo = async (idProyecto: number) => {
    try {
      setCargando(true);
      setProyectoSeleccionado(idProyecto);
      setPropuesta(null);
      setMsgConfirmacion("");
      setErrConfirmacion("");

      const data = await proponerEquipoOptima(idProyecto);
      setPropuesta(data);
    } catch (error) {
      console.error("Error OPTIMA Team:", error);
      setPropuesta(null);
    } finally {
      setCargando(false);
    }
  };

  const confirmarAsignacion = async () => {
    if (!proyectoSeleccionado || !propuesta) return;

    setConfirmando(true);
    setMsgConfirmacion("");
    setErrConfirmacion("");

    try {
      const data = await confirmarPropuestaOptima(
        proyectoSeleccionado,
        `OPTIMA - ${propuesta.proyecto}`,
      );
      setMsgConfirmacion(data.mensaje);
    } catch (err) {
      setErrConfirmacion(
        err instanceof Error
          ? err.message
          : "No se pudo confirmar la asignación",
      );
    } finally {
      setConfirmando(false);
    }
  };

  const tareaActual = tareas.find((t) => t.id_tarea === tareaSeleccionada);
  const candidatosElegibles = candidatos.filter((c) => c.elegible);
  const mejorCandidato = candidatos.length > 0 ? candidatos[0] : null;
  const promedioCompatibilidad =
    candidatos.length > 0
      ? candidatos.reduce((total, c) => total + (c.compatibilidad ?? 0), 0) /
        candidatos.length
      : 0;

  return (
    <section className="optima-page">
      {/* HERO */}
      <div className="optima-hero">
        <div className="optima-hero-glow" />
        <div className="optima-hero-content">
          <div className="optima-engine-label">
            <span className="optima-engine-dot" />
            OPTIMA ENGINE
          </div>
          <h2>
            Optimización
            <span> inteligente</span>
          </h2>
          <p>
            Analiza capacidades, habilidades y disponibilidad para encontrar las
            personas más adecuadas para cada tarea o armar el mejor equipo para
            un proyecto.
          </p>
        </div>
        <div className="optima-hero-symbol">
          <span>✦</span>
        </div>
      </div>

      {/* TABS */}
      <div className="optima-tabs">
        <button
          type="button"
          className={modo === "tarea" ? "optima-tab active" : "optima-tab"}
          onClick={() => {
            setModo("tarea");
            setPropuesta(null);
            setProyectoSeleccionado(null);
            setMsgConfirmacion("");
            setErrConfirmacion("");
          }}
        >
          Análisis por tarea
        </button>
        <button
          type="button"
          className={modo === "equipo" ? "optima-tab active" : "optima-tab"}
          onClick={() => {
            setModo("equipo");
            setCandidatos([]);
            setTareaSeleccionada(null);
          }}
        >
          Propuesta de equipo
        </button>
      </div>

      {/* ===================== MODO TAREA ===================== */}
      {modo === "tarea" && (
        <>
          <div className="optima-control">
            <div className="optima-control-title">
              <div className="optima-control-icon">⌁</div>
              <div>
                <span>ANÁLISIS DE TAREA</span>
                <h3>Selecciona una tarea y el alcance</h3>
              </div>
            </div>

            <div className="optima-filters-row">
              <div className="optima-select-wrapper">
                <select
                  value={tareaSeleccionada ?? ""}
                  onChange={(evento) => {
                    const idTarea = Number(evento.target.value);
                    if (idTarea) {
                      evaluarTarea(idTarea, alcance);
                    } else {
                      setTareaSeleccionada(null);
                      setCandidatos([]);
                    }
                  }}
                >
                  <option value="">Selecciona una tarea para analizar</option>
                  {tareas.map((tarea) => (
                    <option key={tarea.id_tarea} value={tarea.id_tarea}>
                      {tarea.nombre}
                    </option>
                  ))}
                </select>
                <span className="optima-select-arrow">⌄</span>
              </div>

              <div className="optima-select-wrapper">
                <select
                  value={alcance}
                  onChange={(e) => {
                    const nuevo = e.target.value as AlcanceOptima;
                    setAlcance(nuevo);
                    if (tareaSeleccionada) {
                      evaluarTarea(tareaSeleccionada, nuevo);
                    }
                  }}
                >
                  <option value="equipo">Alcance: equipo de la tarea</option>
                  <option value="proyecto">Alcance: proyecto</option>
                  <option value="organizacion">Alcance: organización</option>
                </select>
                <span className="optima-select-arrow">⌄</span>
              </div>
            </div>
          </div>

          {tareaActual && !cargando && candidatos.length > 0 && (
            <div className="optima-task-summary">
              <div className="optima-task-main">
                <span className="optima-label">TAREA ANALIZADA</span>
                <h3>{tareaActual.nombre}</h3>
                <p>OPTIMA evaluó {textoAlcance(alcance)}.</p>
              </div>
              <div className="optima-summary-metrics">
                <div>
                  <span>CANDIDATOS</span>
                  <strong>{candidatos.length}</strong>
                </div>
                <div>
                  <span>ELEGIBLES</span>
                  <strong className="metric-success">
                    {candidatosElegibles.length}
                  </strong>
                </div>
                <div>
                  <span>COMPATIBILIDAD MEDIA</span>
                  <strong>{promedioCompatibilidad.toFixed(0)}%</strong>
                </div>
                <div>
                  <span>MEJOR PUNTUACIÓN</span>
                  <strong className="metric-optima">
                    {mejorCandidato?.puntuacion_optima?.toFixed(1) ?? "0.0"}
                  </strong>
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {/* ===================== MODO EQUIPO ===================== */}
      {modo === "equipo" && (
        <div className="optima-control">
          <div className="optima-control-title">
            <div className="optima-control-icon">◈</div>
            <div>
              <span>OPTIMA TEAM</span>
              <h3>Selecciona un proyecto</h3>
            </div>
          </div>

          <div className="optima-select-wrapper">
            <select
              value={proyectoSeleccionado ?? ""}
              onChange={(e) => {
                const id = Number(e.target.value);
                if (id) {
                  analizarEquipo(id);
                } else {
                  setProyectoSeleccionado(null);
                  setPropuesta(null);
                  setMsgConfirmacion("");
                  setErrConfirmacion("");
                }
              }}
            >
              <option value="">Selecciona un proyecto</option>
              {proyectos.map((p) => (
                <option key={p.id_proyecto} value={p.id_proyecto}>
                  {p.nombre}
                </option>
              ))}
            </select>
            <span className="optima-select-arrow">⌄</span>
          </div>
        </div>
      )}

      {/* LOADING */}
      {cargando && (
        <div className="optima-loading">
          <div className="optima-loading-icon">
            <span>✦</span>
          </div>
          <div>
            <strong>
              {modo === "tarea"
                ? "Analizando candidatos"
                : "Armando propuesta de equipo"}
            </strong>
            <p>
              OPTIMA está evaluando habilidades, experiencia y disponibilidad.
            </p>
          </div>
          <div className="optima-loading-bar">
            <span />
          </div>
        </div>
      )}

      {/* RESULTADOS TAREA */}
      {modo === "tarea" && !cargando && candidatos.length > 0 && (
        <div className="optima-results">
          <div className="optima-results-heading">
            <div>
              <span className="optima-label">RESULTADOS DEL MOTOR</span>
              <h3>Candidatos analizados</h3>
            </div>
            <div className="optima-results-count">
              {candidatos.length} candidatos
            </div>
          </div>

          <div className="optima-grid">
            {candidatos.map((candidato) => {
              const esRecomendado =
                candidato.ranking === 1 && candidato.elegible;
              const esMejorAlternativa =
                candidato.ranking === 1 && !candidato.elegible;

              return (
                <article
                  className={`optima-card ${
                    candidato.elegible
                      ? "optima-card-elegible"
                      : "optima-card-no-elegible"
                  } ${
                    esRecomendado
                      ? "optima-card-recommended"
                      : esMejorAlternativa
                        ? "optima-card-alternative"
                        : ""
                  }`}
                  key={candidato.id_persona}
                >
                  <div className="optima-card-top">
                    <div className="optima-person">
                      <div className="optima-person-avatar">
                        {candidato.persona.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <span className="optima-person-label">CANDIDATO</span>
                        <h4>{candidato.persona}</h4>
                      </div>
                    </div>
                    {candidato.ranking && (
                      <div
                        className={`optima-rank ${
                          candidato.ranking === 1 ? "optima-rank-first" : ""
                        }`}
                      >
                        <span>#</span>
                        {candidato.ranking}
                      </div>
                    )}
                  </div>

                  <div className="optima-status-row">
                    {esRecomendado && (
                      <span className="optima-badge optima-badge-recommended">
                        <span>★</span> RECOMENDADO
                      </span>
                    )}
                    {esMejorAlternativa && (
                      <span className="optima-badge optima-badge-alternative">
                        <span>◆</span> MEJOR ALTERNATIVA
                      </span>
                    )}
                    <span
                      className={`optima-status ${
                        candidato.elegible
                          ? "optima-status-success"
                          : "optima-status-danger"
                      }`}
                    >
                      <span className="optima-status-dot" />
                      {candidato.elegible ? "ELEGIBLE" : "NO ELEGIBLE"}
                    </span>
                  </div>

                  <div className="optima-score-box">
                    <div>
                      <span>PUNTUACIÓN OPTIMA</span>
                      <small>Evaluación global del candidato</small>
                    </div>
                    <strong>
                      {candidato.puntuacion_optima?.toFixed(2) ?? "0.00"}
                    </strong>
                  </div>

                  <div className="optima-metrics">
                    <div className="optima-metric">
                      <div className="optima-metric-head">
                        <span>Compatibilidad</span>
                        <strong>
                          {candidato.compatibilidad?.toFixed(0) ?? "0"}%
                        </strong>
                      </div>
                      <div className="optima-progress">
                        <span
                          style={{
                            width: `${Math.min(candidato.compatibilidad ?? 0, 100)}%`,
                          }}
                        />
                      </div>
                    </div>
                    <div className="optima-metric">
                      <div className="optima-metric-head">
                        <span>Experiencia</span>
                        <strong>
                          {candidato.experiencia?.toFixed(0) ?? "0"}%
                        </strong>
                      </div>
                      <div className="optima-progress">
                        <span
                          style={{
                            width: `${Math.min(candidato.experiencia ?? 0, 100)}%`,
                          }}
                        />
                      </div>
                    </div>
                    <div className="optima-metric">
                      <div className="optima-metric-head">
                        <span>Disponibilidad</span>
                        <strong>
                          {candidato.disponibilidad?.toFixed(0) ?? "0"}%
                        </strong>
                      </div>
                      <div className="optima-progress">
                        <span
                          style={{
                            width: `${Math.min(candidato.disponibilidad ?? 0, 100)}%`,
                          }}
                        />
                      </div>
                    </div>
                  </div>

                  <div className="optima-capacity">
                    <div>
                      <span>CAPACIDAD SEMANAL</span>
                      <strong>{candidato.capacidad_horas_semana} h</strong>
                    </div>
                    <div>
                      <span>CARGA ACTUAL</span>
                      <strong>
                        {candidato.horas_carga_actual?.toFixed(1) ?? "0.0"} %
                      </strong>
                    </div>
                    <div>
                      <span>HABILIDADES</span>
                      <strong>
                        {candidato.habilidades_cumplidas}/
                        {candidato.habilidades_requeridas}
                      </strong>
                    </div>
                  </div>

                  <div className="optima-skills">
                    <div className="optima-section-title">
                      Habilidades evaluadas
                    </div>
                    {candidato.habilidades_ok && (
                      <div className="skill-row skill-ok">
                        <span className="skill-icon">✓</span>
                        <div>
                          <span>CUMPLIDAS</span>
                          <p>{candidato.habilidades_ok}</p>
                        </div>
                      </div>
                    )}
                    {candidato.habilidades_no_registradas && (
                      <div className="skill-row skill-missing">
                        <span className="skill-icon">!</span>
                        <div>
                          <span>NO REGISTRADAS</span>
                          <p>{candidato.habilidades_no_registradas}</p>
                        </div>
                      </div>
                    )}
                    {candidato.habilidades_nivel_insuficiente && (
                      <div className="skill-row skill-insufficient">
                        <span className="skill-icon">↓</span>
                        <div>
                          <span>NIVEL INSUFICIENTE</span>
                          <p>{candidato.habilidades_nivel_insuficiente}</p>
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="optima-explanation">
                    <div className="optima-explanation-title">
                      <span>¿POR QUÉ ESTE RESULTADO?</span>
                    </div>
                    <p>{candidato.explicacion}</p>
                  </div>
                </article>
              );
            })}
          </div>
        </div>
      )}

      {/* RESULTADOS EQUIPO */}
      {modo === "equipo" && !cargando && propuesta && (
        <div className="optima-team-results">
          <div className="optima-task-summary">
            <div className="optima-task-main">
              <span className="optima-label">PROYECTO ANALIZADO</span>
              <h3>{propuesta.proyecto}</h3>
              <p>{propuesta.explicacion}</p>
            </div>
            <div className="optima-summary-metrics">
              <div>
                <span>COBERTURA</span>
                <strong>{propuesta.cobertura}%</strong>
              </div>
              <div>
                <span>INTEGRANTES</span>
                <strong>{propuesta.integrantes_recomendados}</strong>
              </div>
              <div>
                <span>HABILIDADES</span>
                <strong>
                  {propuesta.habilidades_cubiertas}/
                  {propuesta.habilidades_requeridas}
                </strong>
              </div>
              <div>
                <span>¿CREABLE?</span>
                <strong
                  className={
                    propuesta.puede_crearse ? "metric-success" : "metric-optima"
                  }
                >
                  {propuesta.puede_crearse ? "Sí" : "Ajustar"}
                </strong>
              </div>
            </div>
          </div>

          {propuesta.lider && (
            <div className="optima-team-block">
              <h3>Líder propuesto</h3>
              <article className="optima-card optima-card-recommended">
                <div className="optima-card-top">
                  <div className="optima-person">
                    <div className="optima-person-avatar">
                      {propuesta.lider.persona.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <span className="optima-person-label">LÍDER</span>
                      <h4>{propuesta.lider.persona}</h4>
                    </div>
                  </div>
                  <div className="optima-rank optima-rank-first">
                    {propuesta.lider.puntuacion_liderazgo.toFixed(1)}
                  </div>
                </div>
                <p className="optima-team-meta">
                  Confianza:{" "}
                  {propuesta.lider.confianza ??
                    propuesta.confianza_liderazgo ??
                    "—"}{" "}
                  · Compat {propuesta.lider.compatibilidad}% · Exp{" "}
                  {propuesta.lider.experiencia}% · Disp{" "}
                  {propuesta.lider.disponibilidad}%
                </p>
                {propuesta.lider.explicacion && (
                  <div className="optima-explanation">
                    <p>{propuesta.lider.explicacion}</p>
                  </div>
                )}
              </article>
            </div>
          )}

          {propuesta.lider_alternativo && (
            <div className="optima-team-block">
              <h3>Líder alternativo</h3>
              <article className="optima-card optima-card-alternative">
                <div className="optima-card-top">
                  <div className="optima-person">
                    <div className="optima-person-avatar">
                      {propuesta.lider_alternativo.persona
                        .charAt(0)
                        .toUpperCase()}
                    </div>
                    <div>
                      <span className="optima-person-label">ALTERNATIVA</span>
                      <h4>{propuesta.lider_alternativo.persona}</h4>
                    </div>
                  </div>
                  <div className="optima-rank">
                    {propuesta.lider_alternativo.puntuacion_liderazgo.toFixed(
                      1,
                    )}
                  </div>
                </div>
                {propuesta.lider_alternativo.explicacion && (
                  <div className="optima-explanation">
                    <p>{propuesta.lider_alternativo.explicacion}</p>
                  </div>
                )}
              </article>
            </div>
          )}

          <div className="optima-team-block">
            <h3>Integrantes propuestos</h3>
            <div className="optima-grid">
              {propuesta.integrantes.map((int) => (
                <article
                  className="optima-card optima-card-elegible"
                  key={int.id_persona}
                >
                  <div className="optima-card-top">
                    <div className="optima-person">
                      <div className="optima-person-avatar">
                        {int.persona.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <span className="optima-person-label">INTEGRANTE</span>
                        <h4>{int.persona}</h4>
                      </div>
                    </div>
                    <div className="optima-rank">
                      {int.puntuacion_equipo.toFixed(1)}
                    </div>
                  </div>
                  <div className="optima-metrics">
                    <div className="optima-metric">
                      <div className="optima-metric-head">
                        <span>Compatibilidad</span>
                        <strong>{int.compatibilidad}%</strong>
                      </div>
                      <div className="optima-progress">
                        <span
                          style={{
                            width: `${Math.min(int.compatibilidad, 100)}%`,
                          }}
                        />
                      </div>
                    </div>
                    <div className="optima-metric">
                      <div className="optima-metric-head">
                        <span>Experiencia</span>
                        <strong>{int.experiencia}%</strong>
                      </div>
                      <div className="optima-progress">
                        <span
                          style={{
                            width: `${Math.min(int.experiencia, 100)}%`,
                          }}
                        />
                      </div>
                    </div>
                    <div className="optima-metric">
                      <div className="optima-metric-head">
                        <span>Disponibilidad</span>
                        <strong>{int.disponibilidad}%</strong>
                      </div>
                      <div className="optima-progress">
                        <span
                          style={{
                            width: `${Math.min(int.disponibilidad, 100)}%`,
                          }}
                        />
                      </div>
                    </div>
                  </div>
                  {int.contribucion && (
                    <div className="optima-explanation">
                      <p>{int.contribucion}</p>
                    </div>
                  )}
                  {int.habilidades_ok && (
                    <div className="skill-row skill-ok">
                      <span className="skill-icon">✓</span>
                      <div>
                        <span>CUBRE</span>
                        <p>{int.habilidades_ok}</p>
                      </div>
                    </div>
                  )}
                </article>
              ))}
            </div>
          </div>

          <div className="optima-team-block optima-team-insights">
            {propuesta.habilidades_faltantes && (
              <p>
                <strong>Habilidades faltantes:</strong>{" "}
                {propuesta.habilidades_faltantes}
              </p>
            )}
            {propuesta.riesgos_detectados &&
              propuesta.riesgos_detectados.length > 0 && (
                <>
                  <h3>Riesgos detectados</h3>
                  <ul>
                    {propuesta.riesgos_detectados.map((r, i) => (
                      <li key={i}>{r}</li>
                    ))}
                  </ul>
                </>
              )}
            {propuesta.recomendaciones &&
              propuesta.recomendaciones.length > 0 && (
                <>
                  <h3>Recomendaciones</h3>
                  <ul>
                    {propuesta.recomendaciones.map((r, i) => (
                      <li key={i}>{r}</li>
                    ))}
                  </ul>
                </>
              )}
          </div>

          <div className="optima-confirm-box">
            <div>
              <strong>Confirmar propuesta</strong>
              <p>
                Crea el equipo, agrega integrantes y asigna las tareas del
                proyecto a las personas recomendadas por OPTIMA.
              </p>
            </div>
            <button
              type="button"
              className="optima-confirm-btn"
              onClick={confirmarAsignacion}
              disabled={confirmando}
            >
              {confirmando ? "Asignando..." : "Confirmar y asignar equipo"}
            </button>
            {msgConfirmacion && (
              <p className="optima-confirm-ok">{msgConfirmacion}</p>
            )}
            {errConfirmacion && (
              <p className="optima-confirm-err">{errConfirmacion}</p>
            )}
          </div>
        </div>
      )}

      {/* EMPTY STATES */}
      {modo === "tarea" &&
        !cargando &&
        tareaSeleccionada &&
        candidatos.length === 0 && (
          <div className="optima-empty">
            <div className="optima-empty-icon">✦</div>
            <h3>No fue posible generar el análisis</h3>
            <p>
              Prueba otro alcance (proyecto u organización) o verifica
              habilidades y personas activas.
            </p>
          </div>
        )}

      {modo === "tarea" && !cargando && !tareaSeleccionada && (
        <div className="optima-empty optima-empty-start">
          <div className="optima-empty-orbit">
            <span>✦</span>
          </div>
          <h3>Listo para optimizar</h3>
          <p>
            Selecciona una tarea y el alcance (equipo, proyecto u organización)
            para el ranking.
          </p>
        </div>
      )}

      {modo === "equipo" && !cargando && !proyectoSeleccionado && (
        <div className="optima-empty optima-empty-start">
          <div className="optima-empty-orbit">
            <span>◈</span>
          </div>
          <h3>Propuesta de equipo</h3>
          <p>
            Selecciona un proyecto para que OPTIMA proponga líder e integrantes
            según habilidades y disponibilidad.
          </p>
        </div>
      )}

      {modo === "equipo" && !cargando && proyectoSeleccionado && !propuesta && (
        <div className="optima-empty">
          <div className="optima-empty-icon">✦</div>
          <h3>No se pudo generar la propuesta</h3>
          <p>
            Verifica que el proyecto tenga tareas con habilidades y personas
            disponibles en la organización.
          </p>
        </div>
      )}
    </section>
  );
}

export default Optima;
