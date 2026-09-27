import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

import "./Header.css";

interface InformacionPagina {
  titulo: string;
  descripcion: string;
}

function obtenerInformacionPagina(ruta: string): InformacionPagina {
  if (ruta.startsWith("/proyectos")) {
    return {
      titulo: "Proyectos",
      descripcion: "Gestiona y supervisa los proyectos de la organización.",
    };
  }

  if (ruta.startsWith("/personas")) {
    return {
      titulo: "Personas",
      descripcion: "Consulta y administra el talento de la organización.",
    };
  }

  if (ruta.startsWith("/equipos")) {
    return {
      titulo: "Equipos",
      descripcion: "Organiza personas y capacidades por proyecto.",
    };
  }

  if (ruta.startsWith("/tareas")) {
    return {
      titulo: "Tareas",
      descripcion: "Supervisa el trabajo y avance de los equipos.",
    };
  }

  if (ruta.startsWith("/usuarios")) {
    return {
      titulo: "Usuarios",
      descripcion: "Administra las cuentas y permisos de la organización.",
    };
  }

  if (ruta.startsWith("/optima")) {
    return {
      titulo: "OPTIMA",
      descripcion: "Motor inteligente para la optimización organizacional.",
    };
  }

  return {
    titulo: "Dashboard",
    descripcion: "Visión general del estado de tu organización.",
  };
}

function obtenerNombreRol(idRol: number | undefined): string {
  switch (idRol) {
    case 1:
      return "Administrador";
    case 2:
      return "Líder de proyecto";
    case 3:
      return "Secretario";
    case 4:
      return "Empleado";
    default:
      return "Usuario";
  }
}

function Header() {
  const { usuario, cerrarSesion } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const informacionPagina = obtenerInformacionPagina(location.pathname);

  const manejarCerrarSesion = () => {
    cerrarSesion();
    navigate("/login", { replace: true });
  };

  const inicial = usuario?.nombre_usuario?.charAt(0).toUpperCase() ?? "U";

  return (
    <header className="header">
      <div className="header-page-info">
        <span className="header-breadcrumb">
          FLOWOS / {informacionPagina.titulo}
        </span>

        <div className="header-title-row">
          <h1>{informacionPagina.titulo}</h1>
        </div>

        <p>{informacionPagina.descripcion}</p>
      </div>

      <div className="header-actions">
        <div className="header-system-status">
          <span className="header-status-dot" />
          <span>Sistema activo</span>
        </div>

        <div className="header-divider" />

        {usuario && (
          <div className="header-user">
            <div className="header-user-info">
              <strong>{usuario.nombre_usuario}</strong>
              <span>{obtenerNombreRol(usuario.id_rol)}</span>
            </div>

            <div className="header-user-avatar">{inicial}</div>
          </div>
        )}

        <button
          type="button"
          className="logout-button"
          onClick={manejarCerrarSesion}
          title="Cerrar sesión"
        >
          <span>↪</span>
          <span>Cerrar sesión</span>
        </button>
      </div>
    </header>
  );
}

export default Header;
