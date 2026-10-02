import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

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
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    const cargar = async () => {
      setCargando(true);
      try {
        const [p, pe, e, t] = await Promise.all([
          obtenerProyectos(),
          obtenerPersonas(),
          obtenerEquipos(),
          obtenerTareas(),
        ]);
        setProyectos(p);
        setPersonas(pe);
        setEquipos(e);
        setTareas(t);
      } catch (error) {
        console.error("Error al cargar dashboard:", error);
      } finally {
        setCargando(false);
      }
    };
    cargar();
  }, []);

  const proyectosActivos = proyectos.filter(
    (p) => p.estado?.toUpperCase() === "ACTIVO",
  ).length;

  const pendientes = tareas.filter(
    (t) => t.estado?.toUpperCase() === "PENDIENTE",
  ).length;
  const enProgreso = tareas.filter((t) =>
    t.estado?.toUpperCase().includes("PROGRESO"),
  ).length;
  const finalizadas = tareas.filter((t) =>
    ["FINALIZADA", "COMPLETADA"].includes(t.estado?.toUpperCase() || ""),
  ).length;

  if (cargando) {
    return <div className="dash-msg">Cargando resumen...</div>;
  }

  return (
    <section className="dash-page">
      <div className="dash-hero">
        <div>
          <span className="dash-eyebrow">FLOWOS · ADMIN</span>
          <h2>Resumen general</h2>
          <p>Estado actual de tu organización de un vistazo.</p>
        </div>
      </div>

      <div className="dash-cards">
        <Link to="/proyectos" className="dash-card">
          <span className="dash-card-label">Proyectos activos</span>
          <strong>{proyectosActivos}</strong>
          <p>{proyectos.length} en total</p>
        </Link>

        <Link to="/personas" className="dash-card">
          <span className="dash-card-label">Personas</span>
          <strong>{personas.length}</strong>
          <p>Registradas en la org</p>
        </Link>

        <Link to="/equipos" className="dash-card">
          <span className="dash-card-label">Equipos</span>
          <strong>{equipos.length}</strong>
          <p>Grupos de trabajo</p>
        </Link>

        <Link to="/tareas" className="dash-card">
          <span className="dash-card-label">Tareas</span>
          <strong>{tareas.length}</strong>
          <p>En el sistema</p>
        </Link>
      </div>

      <div className="dash-section">
        <div className="dash-section-head">
          <h3>Resumen de tareas</h3>
          <Link to="/tareas" className="dash-link">
            Ver todas →
          </Link>
        </div>

        <div className="dash-task-grid">
          <div className="dash-task-item">
            <span>Total</span>
            <strong>{tareas.length}</strong>
          </div>
          <div className="dash-task-item warn">
            <span>Pendientes</span>
            <strong>{pendientes}</strong>
          </div>
          <div className="dash-task-item info">
            <span>En progreso</span>
            <strong>{enProgreso}</strong>
          </div>
          <div className="dash-task-item ok">
            <span>Finalizadas</span>
            <strong>{finalizadas}</strong>
          </div>
        </div>
      </div>

      <div className="dash-section">
        <div className="dash-section-head">
          <h3>Accesos rápidos</h3>
        </div>
        <div className="dash-quick">
          <Link to="/optima" className="dash-quick-item accent">
            <strong>OPTIMA</strong>
            <span>Optimizar equipos y tareas</span>
          </Link>
          <Link to="/proyectos" className="dash-quick-item">
            <strong>Proyectos</strong>
            <span>Gestionar iniciativas</span>
          </Link>
          <Link to="/usuarios" className="dash-quick-item">
            <strong>Usuarios</strong>
            <span>Cuentas y permisos</span>
          </Link>
        </div>
      </div>
    </section>
  );
}

export default Dashboard;
