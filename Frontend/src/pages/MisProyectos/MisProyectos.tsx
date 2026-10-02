import { useEffect, useState } from "react";
import {
  obtenerMisEquiposPersona,
  obtenerEquipos,
  obtenerProyectos,
  type EquipoPersonaItem,
} from "../../service/api";
import type { Equipo } from "../../types/equipo";
import type { Proyecto } from "../../types/proyecto";
import "./MisProyectos.css";

function MisProyectos() {
  const [proyectos, setProyectos] = useState<Proyecto[]>([]);
  const [equiposPorProyecto, setEquiposPorProyecto] = useState<
    Record<number, string[]>
  >({});
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const cargar = async () => {
      setCargando(true);
      setError("");
      try {
        const [rels, equipos, todosProyectos] = await Promise.all([
          obtenerMisEquiposPersona(),
          obtenerEquipos(),
          obtenerProyectos(),
        ]);

        const mapaEquipos = new Map<number, Equipo>();
        equipos.forEach((e) => mapaEquipos.set(e.id_equipo, e));

        const mapaProyectos = new Map<number, Proyecto>();
        todosProyectos.forEach((p) => mapaProyectos.set(p.id_proyecto, p));

        const idsProyecto = new Set<number>();
        const nombresEquipos: Record<number, string[]> = {};

        rels.forEach((r: EquipoPersonaItem) => {
          if (r.fecha_fin) return; // solo activos

          const eq = mapaEquipos.get(r.id_equipo);
          if (!eq) return;

          idsProyecto.add(eq.id_proyecto);

          if (!nombresEquipos[eq.id_proyecto]) {
            nombresEquipos[eq.id_proyecto] = [];
          }
          if (!nombresEquipos[eq.id_proyecto].includes(eq.nombre)) {
            nombresEquipos[eq.id_proyecto].push(eq.nombre);
          }
        });

        setProyectos(
          [...idsProyecto]
            .map((id) => mapaProyectos.get(id))
            .filter((p): p is Proyecto => p !== undefined),
        );
        setEquiposPorProyecto(nombresEquipos);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Error al cargar proyectos",
        );
      } finally {
        setCargando(false);
      }
    };
    cargar();
  }, []);

  if (cargando) {
    return <div className="mis-proy-msg">Cargando tus proyectos...</div>;
  }

  if (error) {
    return <div className="mis-proy-error">{error}</div>;
  }

  return (
    <div className="mis-proy-page">
      <section className="mis-proy-card">
        <h2>Proyectos donde participas</h2>
        <p className="mis-proy-hint">
          Solo se muestran proyectos vinculados a tus equipos activos.
        </p>

        {proyectos.length === 0 ? (
          <p className="mis-proy-hint">
            Aún no estás asignado a ningún proyecto.
          </p>
        ) : (
          <div className="mis-proy-grid">
            {proyectos.map((p) => (
              <article key={p.id_proyecto} className="mis-proy-item">
                <span className="mis-proy-label">PROYECTO</span>
                <h3>{p.nombre}</h3>
                {p.descripcion && (
                  <p className="mis-proy-desc">{p.descripcion}</p>
                )}
                <div className="mis-proy-meta">
                  <span>ID {p.id_proyecto}</span>
                  {equiposPorProyecto[p.id_proyecto]?.length > 0 && (
                    <span>
                      Equipo(s): {equiposPorProyecto[p.id_proyecto].join(", ")}
                    </span>
                  )}
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

export default MisProyectos;
