import { useEffect, useState } from "react";
import {
  obtenerMisEquiposPersona,
  obtenerEquipos,
  obtenerProyectos,
  obtenerPersonas,
  type EquipoPersonaItem,
} from "../../service/api";
import type { Equipo } from "../../types/equipo";
import type { Proyecto } from "../../types/proyecto";
import type { Persona } from "../../types/persona";
import "./MiEquipo.css";

interface EquipoDetalle {
  id_equipo: number;
  nombre: string;
  id_proyecto: number;
  nombre_proyecto: string;
  miRol: string;
  miDedicacion: number;
  integrantes: {
    id_persona: number;
    nombre: string;
    rol_equipo: string;
    dedicacion: number;
  }[];
}

function MiEquipo() {
  const [equipos, setEquipos] = useState<EquipoDetalle[]>([]);
  const [seleccionado, setSeleccionado] = useState<EquipoDetalle | null>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const cargar = async () => {
      setCargando(true);
      setError("");
      try {
        const [misRels, todosEquipos, proyectos, personas, todasRels] =
          await Promise.all([
            obtenerMisEquiposPersona(),
            obtenerEquipos(),
            obtenerProyectos(),
            obtenerPersonas(),
            // integrantes: usamos lista por equipo vía fetch individual sería mejor;
            // si no hay endpoint bulk, filtramos con GET por cada equipo más abajo
            Promise.resolve([] as EquipoPersonaItem[]),
          ]);

        const mapaEquipos = new Map<number, Equipo>();
        todosEquipos.forEach((e) => mapaEquipos.set(e.id_equipo, e));

        const mapaProyectos = new Map<number, Proyecto>();
        proyectos.forEach((p) => mapaProyectos.set(p.id_proyecto, p));

        const mapaPersonas = new Map<number, Persona>();
        personas.forEach((p) => mapaPersonas.set(p.id_persona, p));

        const activos = misRels.filter((r) => !r.fecha_fin);
        const detalle: EquipoDetalle[] = [];

        for (const r of activos) {
          const eq = mapaEquipos.get(r.id_equipo);
          if (!eq) continue;

          const proy = mapaProyectos.get(eq.id_proyecto);

          // Integrantes del equipo
          let integrantesRel: EquipoPersonaItem[] = [];
          try {
            const res = await fetch(
              `http://127.0.0.1:8000/equipos-personas/equipo/${r.id_equipo}`,
              {
                headers: {
                  "Content-Type": "application/json",
                  Authorization: `Bearer ${localStorage.getItem("flowos_token") || ""}`,
                },
              },
            );
            if (res.ok) {
              integrantesRel = await res.json();
            }
          } catch {
            integrantesRel = [];
          }

          detalle.push({
            id_equipo: eq.id_equipo,
            nombre: eq.nombre,
            id_proyecto: eq.id_proyecto,
            nombre_proyecto: proy?.nombre ?? `Proyecto #${eq.id_proyecto}`,
            miRol: r.rol_equipo,
            miDedicacion: Number(r.dedicacion),
            integrantes: integrantesRel
              .filter((i) => !i.fecha_fin)
              .map((i) => {
                const per = mapaPersonas.get(i.id_persona);
                return {
                  id_persona: i.id_persona,
                  nombre: per
                    ? `${per.nombre} ${per.apellido}`
                    : `Persona #${i.id_persona}`,
                  rol_equipo: i.rol_equipo,
                  dedicacion: Number(i.dedicacion),
                };
              }),
          });
        }

        setEquipos(detalle);
        if (detalle.length > 0) setSeleccionado(detalle[0]);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Error al cargar equipos",
        );
      } finally {
        setCargando(false);
      }
    };
    cargar();
  }, []);

  if (cargando) {
    return <div className="mi-eq-msg">Cargando tus equipos...</div>;
  }

  if (error) {
    return <div className="mi-eq-error">{error}</div>;
  }

  return (
    <div className="mi-eq-page">
      <div className="mi-eq-layout">
        <section className="mi-eq-card">
          <h2>Mis equipos</h2>
          <p className="mi-eq-hint">
            Selecciona un equipo para ver integrantes.
          </p>

          {equipos.length === 0 ? (
            <p className="mi-eq-hint">No perteneces a ningún equipo activo.</p>
          ) : (
            <ul className="mi-eq-ul">
              {equipos.map((e) => (
                <li key={e.id_equipo}>
                  <button
                    type="button"
                    className={
                      seleccionado?.id_equipo === e.id_equipo
                        ? "mi-eq-item active"
                        : "mi-eq-item"
                    }
                    onClick={() => setSeleccionado(e)}
                  >
                    <strong>{e.nombre}</strong>
                    <span>
                      {e.nombre_proyecto} · {e.miRol}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="mi-eq-card">
          {!seleccionado ? (
            <p className="mi-eq-hint">Elige un equipo.</p>
          ) : (
            <>
              <span className="mi-eq-label">EQUIPO</span>
              <h2>{seleccionado.nombre}</h2>
              <p className="mi-eq-hint">
                Proyecto: {seleccionado.nombre_proyecto}
                <br />
                Tu rol: {seleccionado.miRol} · Dedicación:{" "}
                {seleccionado.miDedicacion}%
              </p>

              <h3 className="mi-eq-sub">Integrantes</h3>
              {seleccionado.integrantes.length === 0 ? (
                <p className="mi-eq-hint">No se pudieron cargar integrantes.</p>
              ) : (
                <ul className="mi-eq-members">
                  {seleccionado.integrantes.map((m) => (
                    <li key={m.id_persona}>
                      <strong>{m.nombre}</strong>
                      <span>
                        {m.rol_equipo} · {m.dedicacion}%
                      </span>
                    </li>
                  ))}
                </ul>
              )}

              <div className="mi-eq-chat-placeholder">
                <strong>Chat del equipo</strong>
                <p>Próximamente: mensajería en tiempo real con este grupo.</p>
              </div>
            </>
          )}
        </section>
      </div>
    </div>
  );
}

export default MiEquipo;
