import { useEffect, useState } from "react";

import {
  obtenerEquipos,
  obtenerProyectos,
  obtenerPersonas,
  obtenerPersonasPorEquipo,
  type EquipoPersonaItem,
} from "../../service/api";

import type { Equipo } from "../../types/equipo";
import type { Proyecto } from "../../types/proyecto";
import type { Persona } from "../../types/persona";

import "./Equipos.css";

interface IntegranteVista {
  id_persona: number;
  nombre: string;
  email: string;
  rol_equipo: string;
  dedicacion: number;
  esLider: boolean;
}

function Equipos() {
  const [equipos, setEquipos] = useState<Equipo[]>([]);
  const [proyectos, setProyectos] = useState<Proyecto[]>([]);
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [seleccionado, setSeleccionado] = useState<Equipo | null>(null);
  const [integrantes, setIntegrantes] = useState<IntegranteVista[]>([]);
  const [cargando, setCargando] = useState(true);
  const [cargandoDetalle, setCargandoDetalle] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const cargar = async () => {
      setCargando(true);
      setError("");
      try {
        const [eqs, proys, pers] = await Promise.all([
          obtenerEquipos(),
          obtenerProyectos(),
          obtenerPersonas(),
        ]);
        setEquipos(eqs);
        setProyectos(proys);
        setPersonas(pers);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "No se pudieron cargar equipos",
        );
      } finally {
        setCargando(false);
      }
    };
    cargar();
  }, []);

  const nombreProyecto = (id: number) =>
    proyectos.find((p) => p.id_proyecto === id)?.nombre ?? `Proyecto #${id}`;

  const abrirDetalle = async (equipo: Equipo) => {
    setSeleccionado(equipo);
    setCargandoDetalle(true);
    setIntegrantes([]);

    try {
      const rels = await obtenerPersonasPorEquipo(equipo.id_equipo);
      const mapa = new Map(personas.map((p) => [p.id_persona, p]));

      const vista: IntegranteVista[] = rels
        .filter((r: EquipoPersonaItem) => !r.fecha_fin)
        .map((r) => {
          const p = mapa.get(r.id_persona);
          const rol = (r.rol_equipo || "").toUpperCase();
          const esLider =
            rol.includes("LIDER") ||
            rol.includes("LÍDER") ||
            rol.includes("LEADER");

          return {
            id_persona: r.id_persona,
            nombre: p
              ? `${p.nombre} ${p.apellido}`
              : `Persona #${r.id_persona}`,
            email: p?.email ?? "—",
            rol_equipo: r.rol_equipo,
            dedicacion: Number(r.dedicacion),
            esLider,
          };
        });

      // Líderes primero
      vista.sort((a, b) => Number(b.esLider) - Number(a.esLider));
      setIntegrantes(vista);
    } catch (err) {
      console.error(err);
    } finally {
      setCargandoDetalle(false);
    }
  };

  if (cargando) {
    return <div className="eq-msg">Cargando equipos...</div>;
  }

  if (error) {
    return <div className="eq-error">{error}</div>;
  }

  const lider = integrantes.find((i) => i.esLider) ?? null;

  return (
    <section className="eq-page">
      <div className="eq-hero">
        <div>
          <span className="eq-eyebrow">COLABORACIÓN</span>
          <h2>Equipos</h2>
          <p>
            Revisa los equipos, su proyecto y los integrantes de cada grupo.
          </p>
        </div>
        <div className="eq-hero-stat">
          <strong>{equipos.length}</strong>
          <span>registrados</span>
        </div>
      </div>

      <div className="eq-layout">
        {/* LISTA */}
        <div className="eq-grid">
          {equipos.length === 0 ? (
            <p className="eq-msg">No hay equipos en la organización.</p>
          ) : (
            equipos.map((equipo) => {
              const activo = seleccionado?.id_equipo === equipo.id_equipo;
              return (
                <article
                  key={equipo.id_equipo}
                  className={activo ? "eq-card active" : "eq-card"}
                  onClick={() => abrirDetalle(equipo)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") abrirDetalle(equipo);
                  }}
                >
                  <div className="eq-card-top">
                    <h3>{equipo.nombre}</h3>
                    <span className="eq-badge">{equipo.estado}</span>
                  </div>
                  <p className="eq-proy">
                    {nombreProyecto(equipo.id_proyecto)}
                  </p>
                  {equipo.descripcion && (
                    <p className="eq-desc">{equipo.descripcion}</p>
                  )}
                </article>
              );
            })
          )}
        </div>

        {/* DETALLE */}
        <aside className="eq-detail">
          {!seleccionado ? (
            <div className="eq-detail-empty">
              <span>♧</span>
              <p>Haz clic en un equipo para ver integrantes y roles.</p>
            </div>
          ) : (
            <>
              <span className="eq-eyebrow">DETALLE</span>
              <h2>{seleccionado.nombre}</h2>
              <span className="eq-badge">{seleccionado.estado}</span>
              <p className="eq-detail-proy">
                Proyecto: {nombreProyecto(seleccionado.id_proyecto)}
              </p>
              {seleccionado.descripcion && (
                <p className="eq-desc">{seleccionado.descripcion}</p>
              )}

              {cargandoDetalle ? (
                <p className="eq-msg">Cargando integrantes...</p>
              ) : (
                <>
                  <div className="eq-lider-box">
                    <span className="eq-eyebrow">LÍDER</span>
                    {lider ? (
                      <>
                        <strong>{lider.nombre}</strong>
                        <span>
                          {lider.rol_equipo} · {lider.dedicacion}% ·{" "}
                          {lider.email}
                        </span>
                      </>
                    ) : (
                      <p className="eq-muted">
                        No hay un rol de líder marcado en este equipo.
                      </p>
                    )}
                  </div>

                  <h3 className="eq-section-title">
                    Integrantes ({integrantes.length})
                  </h3>
                  {integrantes.length === 0 ? (
                    <p className="eq-muted">Sin integrantes activos.</p>
                  ) : (
                    <ul className="eq-members">
                      {integrantes.map((m) => (
                        <li key={m.id_persona}>
                          <div>
                            <strong>
                              {m.nombre}
                              {m.esLider ? " · Líder" : ""}
                            </strong>
                            <span>{m.email}</span>
                          </div>
                          <span className="eq-member-meta">
                            {m.rol_equipo} · {m.dedicacion}%
                          </span>
                        </li>
                      ))}
                    </ul>
                  )}

                  <div className="eq-chat-placeholder">
                    <strong>Chat con el líder / equipo</strong>
                    <p>
                      Próximamente: comunicación en tiempo real con el grupo.
                    </p>
                  </div>
                </>
              )}
            </>
          )}
        </aside>
      </div>
    </section>
  );
}

export default Equipos;
