import { useEffect, useState } from "react";

import { obtenerTareas } from "../../service/api";

import type { Tarea } from "../../types/tarea";
import "./Tareas.css";

function Tareas() {
  const [tareas, setTareas] = useState<Tarea[]>([]);

  useEffect(() => {
    obtenerTareas()
      .then((datos) => {
        setTareas(datos);
      })
      .catch((error) => {
        console.error("Error al obtener tareas:", error);
      });
  }, []);

  return (
    <section className="page">
      <div className="page-header">
        <div>
          <h2>Tareas</h2>
          <p>Consulta las tareas y necesidades de los proyectos.</p>
        </div>
      </div>

      <div className="tasks-list">
        {tareas.map((tarea) => (
          <article className="task-card" key={tarea.id_tarea}>
            <div className="task-main">
              <div>
                <h3>{tarea.nombre}</h3>

                <p>{tarea.descripcion || "Sin descripción disponible."}</p>
              </div>

              <span
                className={`task-priority ${tarea.prioridad.toLowerCase()}`}
              >
                {tarea.prioridad}
              </span>
            </div>

            <div className="task-details">
              <span>
                <strong>Proyecto:</strong> #{tarea.id_proyecto}
              </span>

              <span>
                <strong>Equipo:</strong> #{tarea.id_equipo}
              </span>

              <span>
                <strong>Horas:</strong> {tarea.horas_estimadas}
              </span>

              <span>
                <strong>Estado:</strong>{" "}
                <span className={`task-status ${tarea.estado.toLowerCase()}`}>
                  {tarea.estado}
                </span>
              </span>
              <span>
                <strong>Límite:</strong> {tarea.fecha_limite}
              </span>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

export default Tareas;
