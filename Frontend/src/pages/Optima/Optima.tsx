import { useEffect, useState } from "react";

import { obtenerTareas, evaluarTareaOptima } from "../../service/api";

import type { Tarea } from "../../types/tarea";
import type { CandidatoOptima } from "../../types/optima";

import "./Optima.css";

function Optima() {
  const [tareas, setTareas] = useState<Tarea[]>([]);
  const [tareaSeleccionada, setTareaSeleccionada] = useState<number | null>(
    null,
  );

  const [candidatos, setCandidatos] = useState<CandidatoOptima[]>([]);
  const [cargando, setCargando] = useState(false);

  useEffect(() => {
    obtenerTareas()
      .then((datos) => {
        setTareas(datos);
      })
      .catch((error) => {
        console.error("Error al obtener tareas:", error);
      });
  }, []);

  const evaluarTarea = async (idTarea: number) => {
    try {
      setCargando(true);
      setTareaSeleccionada(idTarea);

      const resultados = await evaluarTareaOptima(idTarea);

      const resultadosOrdenados = [...resultados].sort((a, b) => {
        if (a.elegible && !b.elegible) return -1;
        if (!a.elegible && b.elegible) return 1;

        if (a.ranking && b.ranking) {
          return a.ranking - b.ranking;
        }

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

  const tareaActual = tareas.find(
    (tarea) => tarea.id_tarea === tareaSeleccionada,
  );

  const candidatosElegibles = candidatos.filter(
    (candidato) => candidato.elegible,
  );

  const mejorCandidato = candidatos.length > 0 ? candidatos[0] : null;

  const promedioCompatibilidad =
    candidatos.length > 0
      ? candidatos.reduce(
          (total, candidato) => total + (candidato.compatibilidad ?? 0),
          0,
        ) / candidatos.length
      : 0;

  return (
    <section className="optima-page">
      {/* =====================================================
          HERO OPTIMA
      ===================================================== */}

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
            personas más adecuadas para cada tarea.
          </p>
        </div>

        <div className="optima-hero-symbol">
          <span>✦</span>
        </div>
      </div>

      {/* =====================================================
          SELECCIÓN DE TAREA
      ===================================================== */}

      <div className="optima-control">
        <div className="optima-control-title">
          <div className="optima-control-icon">⌁</div>

          <div>
            <span>ANÁLISIS DE TAREA</span>
            <h3>Selecciona una tarea</h3>
          </div>
        </div>

        <div className="optima-select-wrapper">
          <select
            value={tareaSeleccionada ?? ""}
            onChange={(evento) => {
              const idTarea = Number(evento.target.value);

              if (idTarea) {
                evaluarTarea(idTarea);
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
      </div>

      {/* =====================================================
          RESUMEN DE TAREA
      ===================================================== */}

      {tareaActual && !cargando && candidatos.length > 0 && (
        <div className="optima-task-summary">
          <div className="optima-task-main">
            <span className="optima-label">TAREA ANALIZADA</span>

            <h3>{tareaActual.nombre}</h3>

            <p>
              OPTIMA evaluó los integrantes activos del equipo responsable de
              esta tarea.
            </p>
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

      {/* =====================================================
          LOADING
      ===================================================== */}

      {cargando && (
        <div className="optima-loading">
          <div className="optima-loading-icon">
            <span>✦</span>
          </div>

          <div>
            <strong>Analizando candidatos</strong>
            <p>
              OPTIMA está evaluando habilidades, experiencia y disponibilidad.
            </p>
          </div>

          <div className="optima-loading-bar">
            <span />
          </div>
        </div>
      )}

      {/* =====================================================
          RESULTADOS
      ===================================================== */}

      {!cargando && candidatos.length > 0 && (
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
                  {/* =================================================
                      TOP CARD
                  ================================================= */}

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

                  {/* =================================================
                      STATUS
                  ================================================= */}

                  <div className="optima-status-row">
                    {esRecomendado && (
                      <span className="optima-badge optima-badge-recommended">
                        <span>★</span>
                        RECOMENDADO
                      </span>
                    )}

                    {esMejorAlternativa && (
                      <span className="optima-badge optima-badge-alternative">
                        <span>◆</span>
                        MEJOR ALTERNATIVA
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

                  {/* =================================================
                      SCORE
                  ================================================= */}

                  <div className="optima-score-box">
                    <div>
                      <span>PUNTUACIÓN OPTIMA</span>

                      <small>Evaluación global del candidato</small>
                    </div>

                    <strong>
                      {candidato.puntuacion_optima?.toFixed(2) ?? "0.00"}
                    </strong>
                  </div>

                  {/* =================================================
                      METRICAS
                  ================================================= */}

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
                            width: `${Math.min(
                              candidato.compatibilidad ?? 0,
                              100,
                            )}%`,
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
                            width: `${Math.min(
                              candidato.experiencia ?? 0,
                              100,
                            )}%`,
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
                            width: `${Math.min(
                              candidato.disponibilidad ?? 0,
                              100,
                            )}%`,
                          }}
                        />
                      </div>
                    </div>
                  </div>

                  {/* =================================================
                      CAPACIDAD
                  ================================================= */}

                  <div className="optima-capacity">
                    <div>
                      <span>CAPACIDAD SEMANAL</span>
                      <strong>{candidato.capacidad_horas_semana} h</strong>
                    </div>

                    <div>
                      <span>CARGA ACTUAL</span>
                      <strong>
                        {candidato.horas_carga_actual?.toFixed(1) ?? "0.0"} h
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

                  {/* =================================================
                      SKILLS
                  ================================================= */}

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

                  {/* =================================================
                      EXPLICACION
                  ================================================= */}

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

      {/* =====================================================
          EMPTY STATE
      ===================================================== */}

      {!cargando && tareaSeleccionada && candidatos.length === 0 && (
        <div className="optima-empty">
          <div className="optima-empty-icon">✦</div>

          <h3>No fue posible generar el análisis</h3>

          <p>
            Verifica que la tarea tenga habilidades requeridas y que su equipo
            tenga integrantes activos.
          </p>
        </div>
      )}

      {!cargando && !tareaSeleccionada && (
        <div className="optima-empty optima-empty-start">
          <div className="optima-empty-orbit">
            <span>✦</span>
          </div>

          <h3>Listo para optimizar</h3>

          <p>
            Selecciona una tarea y deja que OPTIMA encuentre las mejores
            alternativas disponibles.
          </p>
        </div>
      )}
    </section>
  );
}

export default Optima;
