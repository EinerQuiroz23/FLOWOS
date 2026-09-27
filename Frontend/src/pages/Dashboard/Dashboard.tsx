import { useEffect, useState } from "react";

import {
  obtenerProyectos,
  obtenerPersonas,
  obtenerEquipos,
  obtenerTareas,
} from "../../service/api";

import type { Proyecto } from "../../types/proyecto";
import type { Persona } from "../../types/persona";
import type { Equipo } from "../../types/equipo";
import type { Tarea } from "../../types/tarea";
import "./Dashboard.css";

function Dashboard() {
  const [proyectos, setProyectos] = useState<Proyecto[]>([]);
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [equipos, setEquipos] = useState<Equipo[]>([]);
  const [tareas, setTareas] = useState<Tarea[]>([]);

  useEffect(() => {
    obtenerProyectos()
      .then((datos) => {
        setProyectos(datos);
      })
      .catch((error) => {
        console.error("Error al obtener proyectos:", error);
      });

    obtenerPersonas()
      .then((datos) => {
        console.log("Personas recibidas:", datos);
        setPersonas(datos);
      })
      .catch((error) => {
        console.error("Error al obtener personas:", error);
      });

    obtenerEquipos()
      .then((datos) => {
        console.log("Equipos recibidos:", datos);
        setEquipos(datos);
      })
      .catch((error) => {
        console.error("Error al obtener equipos:", error);
      });

    obtenerTareas()
      .then((datos) => {
        console.log("Tareas recibidas:", datos);
        setTareas(datos);
      })
      .catch((error) => {
        console.error("Error al obtener tareas:", error);
      });
  }, []);

  return (
    <section className="dashboard">
      <div className="dashboard-header">
        <h2>Resumen general</h2>
        <p>Visualiza el estado actual de tu organización.</p>
      </div>

      <div className="dashboard-cards">
        <div className="dashboard-card">
          <span>Proyectos activos</span>

          <strong>
            {
              proyectos.filter((proyecto) => proyecto.estado === "ACTIVO")
                .length
            }
          </strong>

          <p>Proyectos Actualmente En Ejecución</p>
        </div>

        <div className="dashboard-card">
          <span>Personas</span>

          <strong>{personas.length}</strong>

          <p>Personas Registradas En FLOWOS</p>
        </div>

        <div className="dashboard-card">
          <span>Equipos</span>

          <strong>{equipos.length}</strong>

          <p>Equipos Registrados En La Organización</p>
        </div>

        <div className="dashboard-card">
          <span>Tareas</span>

          <strong>{tareas.length}</strong>

          <p>Tareas Registradas En FLOWOS</p>
        </div>
      </div>

      <div className="dashboard-section">
        <h3>Resumen de tareas</h3>

        <div className="task-summary-grid">
          <div className="summary-item">
            <span>Total</span>
            <strong>{tareas.length}</strong>
          </div>

          <div className="summary-item">
            <span>Pendientes</span>
            <strong>
              {tareas.filter((tarea) => tarea.estado === "PENDIENTE").length}
            </strong>
          </div>

          <div className="summary-item">
            <span>En progreso</span>
            <strong>
              {tareas.filter((tarea) => tarea.estado === "EN_PROGRESO").length}
            </strong>
          </div>

          <div className="summary-item">
            <span>Finalizadas</span>
            <strong>
              {tareas.filter((tarea) => tarea.estado === "FINALIZADA").length}
            </strong>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Dashboard;
