import { useEffect, useState } from "react";

import { obtenerPersonas } from "../../service/api";

import type { Persona } from "../../types/persona";
import "./Personas.css";

function Personas() {
  const [personas, setPersonas] = useState<Persona[]>([]);

  useEffect(() => {
    obtenerPersonas()
      .then((datos) => {
        setPersonas(datos);
      })
      .catch((error) => {
        console.error("Error al obtener personas:", error);
      });
  }, []);

  return (
    <section className="page">
      <div className="page-header">
        <div>
          <h2>Personas</h2>
          <p>Consulta las personas registradas en FLOWOS.</p>
        </div>
      </div>

      <div className="people-grid">
        {personas.map((persona) => (
          <article className="person-card" key={persona.id_persona}>
            <div className="person-card-header">
              <div className="person-avatar">
                {persona.nombre.charAt(0)}
                {persona.apellido.charAt(0)}
              </div>

              <div>
                <h3>
                  {persona.nombre} {persona.apellido}
                </h3>

                <span
                  className={
                    persona.estado
                      ? "person-status activo"
                      : "person-status inactivo"
                  }
                >
                  {persona.estado ? "ACTIVO" : "INACTIVO"}
                </span>
              </div>
            </div>

            <div className="person-info">
              <span>{persona.email}</span>

              <span>Capacidad: {persona.capacidad_horas_semana} h/semana</span>

              {persona.telefono && <span>{persona.telefono}</span>}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

export default Personas;
