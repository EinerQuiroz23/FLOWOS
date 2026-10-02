import { useEffect, useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import {
  obtenerMiPersona,
  obtenerMisTareas,
  cambiarNombreUsuario,
  obtenerHabilidades,
  obtenerNivelesHabilidad,
  obtenerMisHabilidades,
  obtenerMisEquiposPersona,
  obtenerEquipos,
  obtenerProyectos,
  type MiTarea,
  type Habilidad,
  type NivelHabilidad,
  type PersonaHabilidad,
  type EquipoPersonaItem,
} from "../../service/api";
import { useAuth } from "../../context/AuthContext";
import type { Persona } from "../../types/persona";
import type { Equipo } from "../../types/equipo";
import type { Proyecto } from "../../types/proyecto";
import "./MiPanel.css";

function MiPanel() {
  const { usuario } = useAuth();

  const [persona, setPersona] = useState<Persona | null>(null);
  const [tareas, setTareas] = useState<MiTarea[]>([]);
  const [misHabilidades, setMisHabilidades] = useState<PersonaHabilidad[]>([]);
  const [catalogoHabilidades, setCatalogoHabilidades] = useState<Habilidad[]>(
    [],
  );
  const [catalogoNiveles, setCatalogoNiveles] = useState<NivelHabilidad[]>([]);
  const [numEquipos, setNumEquipos] = useState(0);
  const [numProyectos, setNumProyectos] = useState(0);

  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  const [nuevoNombre, setNuevoNombre] = useState("");
  const [msgNombre, setMsgNombre] = useState("");
  const [errNombre, setErrNombre] = useState("");
  const [guardandoNombre, setGuardandoNombre] = useState(false);

  useEffect(() => {
    const cargar = async () => {
      setCargando(true);
      setError("");
      try {
        const [p, t, mias, habs, niveles, rels, equipos, proyectos] =
          await Promise.all([
            obtenerMiPersona(),
            obtenerMisTareas(),
            obtenerMisHabilidades(),
            obtenerHabilidades(),
            obtenerNivelesHabilidad(),
            obtenerMisEquiposPersona(),
            obtenerEquipos(),
            obtenerProyectos(),
          ]);

        setPersona(p);
        setTareas(t);
        setMisHabilidades(mias);
        setCatalogoHabilidades(habs);
        setCatalogoNiveles(niveles);

        const mapaEquipos = new Map<number, Equipo>();
        equipos.forEach((e) => mapaEquipos.set(e.id_equipo, e));

        const activos = rels.filter((r: EquipoPersonaItem) => !r.fecha_fin);
        setNumEquipos(activos.length);

        const idsProy = new Set<number>();
        activos.forEach((r) => {
          const eq = mapaEquipos.get(r.id_equipo);
          if (eq) idsProy.add(eq.id_proyecto);
        });
        setNumProyectos(idsProy.size);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Error al cargar el panel",
        );
      } finally {
        setCargando(false);
      }
    };
    cargar();
  }, []);

  useEffect(() => {
    if (usuario?.nombre_usuario) {
      setNuevoNombre(usuario.nombre_usuario);
    }
  }, [usuario]);

  const guardarNombre = async (event: FormEvent) => {
    event.preventDefault();
    setMsgNombre("");
    setErrNombre("");
    setGuardandoNombre(true);
    try {
      const data = await cambiarNombreUsuario(nuevoNombre.trim());
      setMsgNombre(data.mensaje);
      setTimeout(() => window.location.reload(), 800);
    } catch (err) {
      setErrNombre(
        err instanceof Error ? err.message : "No se pudo actualizar el nombre",
      );
    } finally {
      setGuardandoNombre(false);
    }
  };

  const nombreHabilidad = (id: number) =>
    catalogoHabilidades.find((h) => h.id_habilidad === id)?.nombre ?? `#${id}`;

  const nombreNivel = (id: number) =>
    catalogoNiveles.find((n) => n.id_nivel === id)?.nombre ?? `#${id}`;

  if (cargando) {
    return <div className="mi-panel-loading">Cargando tu panel...</div>;
  }

  if (error) {
    return <div className="mi-panel-error">{error}</div>;
  }

  const completadas = tareas.filter((t) =>
    (t.estado_asignacion || t.estado_tarea || "")
      .toUpperCase()
      .includes("COMPLET"),
  ).length;

  return (
    <div className="mi-panel">
      {/* HERO PERFIL */}
      <section className="mi-card mi-perfil mi-perfil-hero">
        <div className="mi-avatar">
          {(persona?.nombre || "U").charAt(0).toUpperCase()}
        </div>
        <div className="mi-perfil-text">
          <span className="mi-eyebrow">TU ESPACIO EN FLOWOS</span>
          <h2>
            {persona?.nombre} {persona?.apellido}
          </h2>
          <p>{persona?.email}</p>
          {persona?.telefono && <p>Tel: {persona.telefono}</p>}
          <p className="mi-meta">
            @{usuario?.nombre_usuario ?? "—"} ·{" "}
            {persona?.capacidad_horas_semana ?? "—"} h/semana disponibles
          </p>
        </div>
      </section>

      {/* STATS */}
      <div className="mi-stats">
        <div className="mi-stat">
          <strong>{tareas.length}</strong>
          <span>Tareas</span>
        </div>
        <div className="mi-stat">
          <strong>{completadas}</strong>
          <span>Completadas</span>
        </div>
        <div className="mi-stat">
          <strong>{numEquipos}</strong>
          <span>Equipos</span>
        </div>
        <div className="mi-stat">
          <strong>{numProyectos}</strong>
          <span>Proyectos</span>
        </div>
        <div className="mi-stat">
          <strong>{misHabilidades.length}</strong>
          <span>Habilidades</span>
        </div>
      </div>

      <div className="mi-panel-grid">
        {/* NOMBRE */}
        <section className="mi-card">
          <h3>Nombre de perfil</h3>
          <p className="mi-empty">Así te ven en FlowOS (no es tu correo).</p>
          <form onSubmit={guardarNombre} className="mi-form-nombre">
            <input
              type="text"
              value={nuevoNombre}
              onChange={(e) => setNuevoNombre(e.target.value)}
              minLength={3}
              maxLength={100}
              required
            />
            <button type="submit" disabled={guardandoNombre}>
              {guardandoNombre ? "Guardando..." : "Guardar"}
            </button>
          </form>
          {msgNombre && <div className="mi-ok">{msgNombre}</div>}
          {errNombre && <div className="mi-panel-error">{errNombre}</div>}
        </section>

        {/* HABILIDADES solo lectura */}
        <section className="mi-card">
          <div className="mi-card-head">
            <h3>Mis habilidades</h3>
            <Link to="/mis-habilidades" className="mi-link">
              Gestionar →
            </Link>
          </div>
          <p className="mi-empty">
            Resumen de tu perfil técnico. Para agregar o editar, usa Mis
            habilidades.
          </p>

          {misHabilidades.length === 0 ? (
            <p className="mi-empty">
              Aún no tienes habilidades.{" "}
              <Link to="/mis-habilidades" className="mi-link-inline">
                Regístralas aquí
              </Link>
              .
            </p>
          ) : (
            <ul className="mi-hab-list">
              {misHabilidades.map((h) => (
                <li key={h.id_persona_habilidad}>
                  <strong>{nombreHabilidad(h.id_habilidad)}</strong>
                  <span>
                    {nombreNivel(h.id_nivel)} · {h.años_experiencia} a
                  </span>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>

      {/* ACCESOS RÁPIDOS */}
      <section className="mi-card">
        <h3>Accesos rápidos</h3>
        <div className="mi-quick">
          <Link to="/mis-tareas" className="mi-quick-item">
            <span>Mis tareas</span>
            <small>{tareas.length} asignadas</small>
          </Link>
          <Link to="/mis-proyectos" className="mi-quick-item">
            <span>Mis proyectos</span>
            <small>{numProyectos} activos</small>
          </Link>
          <Link to="/mi-equipo" className="mi-quick-item">
            <span>Mi equipo</span>
            <small>{numEquipos} equipos</small>
          </Link>
          <Link to="/mis-habilidades" className="mi-quick-item">
            <span>Habilidades</span>
            <small>{misHabilidades.length} registradas</small>
          </Link>
        </div>
      </section>
    </div>
  );
}

export default MiPanel;
