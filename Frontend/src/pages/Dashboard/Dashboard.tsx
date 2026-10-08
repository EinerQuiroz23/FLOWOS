import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
  obtenerProyectos,
  obtenerPersonas,
  obtenerEquipos,
  obtenerTareas,
  listarOrganizaciones,
  type OrganizacionItem,
} from "../../service/api";

import { useAuth } from "../../context/AuthContext";
import { ROLES } from "../../utils/roles";

import type { Proyecto } from "../../types/proyecto";
import type { Persona } from "../../types/persona";
import type { Equipo } from "../../types/equipo";
import type { Tarea } from "../../types/tarea";

import "./Dashboard.css";

function Dashboard() {
  const { usuario } = useAuth();
  const esSuperAdmin = usuario?.id_rol === ROLES.SUPER_ADMIN;
  const esAdmin = usuario?.id_rol === ROLES.ADMIN;
  const esSecretario = usuario?.id_rol === ROLES.SECRETARIO;
  const esLider = usuario?.id_rol === ROLES.LIDER_PROYECTO;

  const [proyectos, setProyectos] = useState<Proyecto[]>([]);
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [equipos, setEquipos] = useState<Equipo[]>([]);
  const [tareas, setTareas] = useState<Tarea[]>([]);
  const [organizaciones, setOrganizaciones] = useState<OrganizacionItem[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const cargar = async () => {
      setCargando(true);
      setError("");
      try {
        if (esSuperAdmin) {
          const orgs = await listarOrganizaciones();
          setOrganizaciones(orgs);
        } else {
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
        }
      } catch (err) {
        console.error("Error al cargar dashboard:", err);
        setError(
          err instanceof Error ? err.message : "No se pudo cargar el resumen",
        );
      } finally {
        setCargando(false);
      }
    };
    cargar();
  }, [esSuperAdmin]);

  if (cargando) {
    return <div className="dash-msg">Cargando resumen...</div>;
  }

  if (error) {
    return <div className="dash-msg">{error}</div>;
  }

  // ========== SUPER ADMIN ==========
  if (esSuperAdmin) {
    const activas = organizaciones.filter((o) => o.estado).length;
    const inactivas = organizaciones.length - activas;

    return (
      <section className="dash-page">
        <div className="dash-hero">
          <div>
            <span className="dash-eyebrow">FLOWOS · PLATAFORMA</span>
            <h2>Panel Super Admin</h2>
            <p>Visión global de organizaciones registradas en FLOWOS.</p>
          </div>
        </div>

        <div className="dash-cards">
          <Link to="/organizaciones" className="dash-card">
            <span className="dash-card-label">Organizaciones</span>
            <strong>{organizaciones.length}</strong>
            <p>Total registradas</p>
          </Link>
          <div className="dash-card">
            <span className="dash-card-label">Activas</span>
            <strong>{activas}</strong>
            <p>En operación</p>
          </div>
          <div className="dash-card">
            <span className="dash-card-label">Inactivas</span>
            <strong>{inactivas}</strong>
            <p>Suspendidas / dadas de baja</p>
          </div>
        </div>

        <div className="dash-section">
          <div className="dash-section-head">
            <h3>Organizaciones recientes</h3>
            <Link to="/organizaciones" className="dash-link">
              Ver todas →
            </Link>
          </div>
          {organizaciones.length === 0 ? (
            <p className="dash-msg">Aún no hay organizaciones.</p>
          ) : (
            <div className="dash-task-grid">
              {organizaciones.slice(0, 6).map((org) => (
                <div key={org.id_organizacion} className="dash-task-item">
                  <span>{org.estado ? "ACTIVA" : "INACTIVA"}</span>
                  <strong style={{ fontSize: "1rem" }}>{org.nombre}</strong>
                  <p style={{ margin: "6px 0 0", fontSize: 12, opacity: 0.7 }}>
                    {org.codigo_organizacion || `ID ${org.id_organizacion}`}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="dash-section">
          <div className="dash-section-head">
            <h3>Accesos rápidos</h3>
          </div>
          <div className="dash-quick">
            <Link to="/organizaciones" className="dash-quick-item accent">
              <strong>Organizaciones</strong>
              <span>Crear, activar o desactivar</span>
            </Link>
          </div>
        </div>
      </section>
    );
  }

  // ========== ADMIN / LÍDER / SECRETARIO ==========
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

  const tituloRol = esSecretario
    ? "SECRETARÍA"
    : esLider
      ? "LIDERAZGO"
      : "ADMIN";

  const subtitulo = esSecretario
    ? "Seguimiento operativo de la organización."
    : "Estado actual de tu organización de un vistazo.";

  return (
    <section className="dash-page">
      <div className="dash-hero">
        <div>
          <span className="dash-eyebrow">FLOWOS · {tituloRol}</span>
          <h2>Resumen general</h2>
          <p>{subtitulo}</p>
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

        {/* ADMIN: OPTIMA + Proyectos + Usuarios */}
        {esAdmin && (
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
        )}

        {/* SECRETARIO / LÍDER: sin OPTIMA ni Usuarios */}
        {(esSecretario || esLider) && (
          <div className="dash-quick">
            <Link to="/proyectos" className="dash-quick-item">
              <strong>Proyectos</strong>
              <span>Consulta de iniciativas</span>
            </Link>
            <Link to="/personas" className="dash-quick-item accent">
              <strong>Personas</strong>
              <span>Talento de la organización</span>
            </Link>
            <Link to="/tareas" className="dash-quick-item">
              <strong>Tareas</strong>
              <span>Seguimiento operativo</span>
            </Link>
            <Link to="/equipos" className="dash-quick-item">
              <strong>Equipos</strong>
              <span>Grupos de trabajo</span>
            </Link>
          </div>
        )}
      </div>
    </section>
  );
}

export default Dashboard;
