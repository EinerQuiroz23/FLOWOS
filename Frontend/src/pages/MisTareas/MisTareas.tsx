import { useEffect, useState } from "react";
import { obtenerMisTareas, type MiTarea } from "../../service/api";
import "./MisTareas.css";

function porcentajePorEstado(estado: string | null): number {
  const e = (estado || "").toUpperCase();
  if (e.includes("COMPLET") || e.includes("FINAL")) return 100;
  if (e.includes("PROGRESO") || e.includes("CURSO")) return 50;
  if (e.includes("ASIGN")) return 15;
  if (e.includes("PEND")) return 5;
  return 25;
}

function textoFaltante(pct: number): string {
  if (pct >= 100) return "Tarea completada.";
  if (pct >= 50) return "Vas a mitad de camino. Sigue con el avance pendiente.";
  if (pct >= 15) return "Tarea asignada. Debes iniciar o continuar el trabajo.";
  return "Pendiente de comenzar.";
}

function MisTareas() {
  const [tareas, setTareas] = useState<MiTarea[]>([]);
  const [seleccionada, setSeleccionada] = useState<MiTarea | null>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const cargar = async () => {
      setCargando(true);
      setError("");
      try {
        const data = await obtenerMisTareas();
        setTareas(data);
        if (data.length > 0) {
          setSeleccionada(data[0]);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Error al cargar tareas");
      } finally {
        setCargando(false);
      }
    };
    cargar();
  }, []);

  if (cargando) {
    return <div className="mis-tareas-msg">Cargando tus tareas...</div>;
  }

  if (error) {
    return <div className="mis-tareas-error">{error}</div>;
  }

  const pct = seleccionada
    ? porcentajePorEstado(
        seleccionada.estado_asignacion || seleccionada.estado_tarea,
      )
    : 0;

  return (
    <div className="mis-tareas-page">
      <div className="mis-tareas-layout">
        {/* LISTA */}
        <section className="mis-tareas-card mis-tareas-lista">
          <h2>Mis tareas</h2>
          <p className="mis-tareas-hint">
            Selecciona una tarea para ver el avance y lo que te corresponde.
          </p>

          {tareas.length === 0 ? (
            <p className="mis-tareas-hint">No tienes tareas asignadas.</p>
          ) : (
            <ul className="mis-tareas-ul">
              {tareas.map((t) => {
                const p = porcentajePorEstado(
                  t.estado_asignacion || t.estado_tarea,
                );
                const activa = seleccionada?.id_asignacion === t.id_asignacion;
                return (
                  <li key={t.id_asignacion}>
                    <button
                      type="button"
                      className={
                        activa ? "mis-tareas-item active" : "mis-tareas-item"
                      }
                      onClick={() => setSeleccionada(t)}
                    >
                      <span className="mis-tareas-item-nombre">
                        {t.nombre_tarea}
                      </span>
                      <span className="mis-tareas-item-meta">
                        {t.estado_asignacion} · {p}%
                      </span>
                    </button>
                  </li>
                );
              })}
            </ul>
          )}
        </section>

        {/* DETALLE */}
        <section className="mis-tareas-card mis-tareas-detalle">
          {!seleccionada ? (
            <p className="mis-tareas-hint">Elige una tarea de la lista.</p>
          ) : (
            <>
              <span className="mis-tareas-label">TAREA SELECCIONADA</span>
              <h2>{seleccionada.nombre_tarea}</h2>

              <div className="mis-tareas-grid-meta">
                <div>
                  <span>Estado asignación</span>
                  <strong>{seleccionada.estado_asignacion}</strong>
                </div>
                <div>
                  <span>Estado tarea</span>
                  <strong>{seleccionada.estado_tarea ?? "—"}</strong>
                </div>
                <div>
                  <span>Prioridad</span>
                  <strong>{seleccionada.prioridad ?? "—"}</strong>
                </div>
                <div>
                  <span>Tu dedicación</span>
                  <strong>{seleccionada.dedicacion}%</strong>
                </div>
                <div>
                  <span>Inicio</span>
                  <strong>{seleccionada.fecha_inicio}</strong>
                </div>
                <div>
                  <span>Límite</span>
                  <strong>{seleccionada.fecha_limite}</strong>
                </div>
                {seleccionada.horas_estimadas != null && (
                  <div>
                    <span>Horas estimadas</span>
                    <strong>{seleccionada.horas_estimadas} h</strong>
                  </div>
                )}
              </div>

              <div className="mis-tareas-avance">
                <div className="mis-tareas-avance-head">
                  <span>Avance orientativo</span>
                  <strong>{pct}%</strong>
                </div>
                <div className="mis-tareas-bar">
                  <span style={{ width: `${pct}%` }} />
                </div>
                <p className="mis-tareas-faltante">{textoFaltante(pct)}</p>
                <p className="mis-tareas-nota">
                  El porcentaje se estima según el estado de la asignación.
                  Cuando el admin/líder actualice el estado, el avance se
                  reflejará aquí.
                </p>
              </div>
            </>
          )}
        </section>
      </div>
    </div>
  );
}

export default MisTareas;
