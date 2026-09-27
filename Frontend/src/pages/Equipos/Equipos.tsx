import { useEffect, useState } from "react";

import { obtenerEquipos } from "../../service/api";

import type { Equipo } from "../../types/equipo";
import "./Equipos.css";

function Equipos() {
  const [equipos, setEquipos] = useState<Equipo[]>([]);

  useEffect(() => {
    obtenerEquipos()
      .then((datos) => {
        setEquipos(datos);
      })
      .catch((error) => {
        console.error("Error al obtener equipos:", error);
      });
  }, []);

  return (
    <section className="page">
      <div className="page-header">
        <div>
          <h2>Equipos</h2>
          <p>Consulta los equipos de trabajo registrados en FLOWOS.</p>
        </div>
      </div>

      <div className="teams-grid">
        {equipos.map((equipo) => (
          <article className="team-card" key={equipo.id_equipo}>
            <div className="team-card-header">
              <div className="team-icon">E</div>

              <div>
                <h3>{equipo.nombre}</h3>

                <span className="team-status">{equipo.estado}</span>
              </div>
            </div>

            <p className="team-description">
              {equipo.descripcion || "Sin descripción disponible."}
            </p>

            <div className="team-info">
              <span>Proyecto asociado: #{equipo.id_proyecto}</span>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

export default Equipos;
