import { useEffect, useState } from "react";

import { obtenerProyectos } from "../../service/api";

import type { Proyecto } from "../../types/proyecto";
import "./Proyectos.css";

function Proyectos() {
  const [proyectos, setProyectos] = useState<Proyecto[]>([]);

  useEffect(() => {
    obtenerProyectos()
      .then((datos) => {
        setProyectos(datos);
      })
      .catch((error) => {
        console.error("Error al obtener proyectos:", error);
      });
  }, []);

  return (
    <section className="page">
      <div className="page-header">
        <div>
          <h2>Proyectos</h2>
          <p>Gestiona y consulta los proyectos de la organización.</p>
        </div>
      </div>

      <div className="projects-grid">
        {proyectos.map((proyecto) => (
          <article className="project-card" key={proyecto.id_proyecto}>
            <div className="project-card-header">
              <h3>{proyecto.nombre}</h3>

              <span
                className={`project-status ${proyecto.estado.toLowerCase()}`}
              >
                {proyecto.estado}
              </span>
            </div>

            <p className="project-description">
              {proyecto.descripcion || "Sin descripción disponible."}
            </p>

            <div className="project-info">
              <span>
                <strong>Inicio:</strong> {proyecto.fecha_inicio}
              </span>

              <span>
                <strong>Límite:</strong> {proyecto.fecha_limite}
              </span>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

export default Proyectos;
