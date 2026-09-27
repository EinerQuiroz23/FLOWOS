import { NavLink } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

import "./Sidebar.css";

interface ItemMenu {
  nombre: string;
  ruta: string;
  roles: number[];
  icono: string;
}

interface SeccionMenu {
  titulo: string;
  items: ItemMenu[];
}

const SECCIONES_MENU: SeccionMenu[] = [
  {
    titulo: "MAIN MENU",
    items: [
      {
        nombre: "Dashboard",
        ruta: "/dashboard",
        roles: [1, 2, 3, 4],
        icono: "⌂",
      },
      {
        nombre: "Proyectos",
        ruta: "/proyectos",
        roles: [1, 2, 3, 4],
        icono: "▣",
      },
      {
        nombre: "Personas",
        ruta: "/personas",
        roles: [1, 2, 3, 4],
        icono: "♙",
      },
      {
        nombre: "Equipos",
        ruta: "/equipos",
        roles: [1, 2, 3, 4],
        icono: "♧",
      },
      {
        nombre: "Tareas",
        ruta: "/tareas",
        roles: [1, 2, 3, 4],
        icono: "✓",
      },
    ],
  },
  {
    titulo: "ADMINISTRATION",
    items: [
      {
        nombre: "Usuarios",
        ruta: "/usuarios",
        roles: [1],
        icono: "⚙",
      },
    ],
  },
  {
    titulo: "OPTIMIZATION",
    items: [
      {
        nombre: "OPTIMA",
        ruta: "/optima",
        roles: [1],
        icono: "✦",
      },
    ],
  },
];

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

function obtenerInicial(nombre: string | undefined): string {
  if (!nombre) {
    return "U";
  }

  return nombre.charAt(0).toUpperCase();
}

function Sidebar() {
  const { usuario } = useAuth();

  return (
    <aside className="sidebar">
      <div className="sidebar-top">
        <div className="sidebar-brand">
          <div className="sidebar-brand-mark">F</div>

          <div className="sidebar-brand-text">
            <strong>FLOWOS</strong>
            <span>Organizational OS</span>
          </div>
        </div>

        {usuario && (
          <div className="sidebar-profile">
            <div className="sidebar-profile-avatar">
              {obtenerInicial(usuario.nombre_usuario)}
            </div>

            <div className="sidebar-profile-info">
              <strong>{usuario.nombre_usuario}</strong>
              <span>{obtenerNombreRol(usuario.id_rol)}</span>
            </div>

            <span className="sidebar-profile-status" />
          </div>
        )}
      </div>

      <nav className="sidebar-navigation">
        {SECCIONES_MENU.map((seccion) => {
          const itemsVisibles = seccion.items.filter((item) =>
            usuario ? item.roles.includes(usuario.id_rol) : false,
          );

          if (itemsVisibles.length === 0) {
            return null;
          }

          return (
            <div className="sidebar-section" key={seccion.titulo}>
              <span className="sidebar-section-title">{seccion.titulo}</span>

              <ul className="sidebar-menu">
                {itemsVisibles.map((item) => (
                  <li key={item.ruta}>
                    <NavLink
                      to={item.ruta}
                      className={({ isActive }) =>
                        isActive
                          ? "sidebar-link sidebar-link-active"
                          : "sidebar-link"
                      }
                    >
                      <span className="sidebar-link-icon">{item.icono}</span>

                      <span className="sidebar-link-name">{item.nombre}</span>
                    </NavLink>
                  </li>
                ))}
              </ul>
            </div>
          );
        })}
      </nav>

      <div className="sidebar-bottom">
        <div className="sidebar-engine">
          <div className="sidebar-engine-icon">✦</div>

          <div>
            <strong>OPTIMA ENGINE</strong>
            <span>Intelligent optimization</span>
          </div>
        </div>

        <div className="sidebar-version">
          <span>FLOWOS</span>
          <small>v1.0</small>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;
