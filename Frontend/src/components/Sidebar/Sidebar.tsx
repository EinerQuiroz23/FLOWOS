import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { blobFotoPersona, subirMiFoto } from "../../service/api";

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
        roles: [1, 2, 3, 5],
        icono: "⌂",
      },
      {
        nombre: "Mi panel",
        ruta: "/mi-panel",
        roles: [4],
        icono: "●",
      },
      {
        nombre: "Mis proyectos",
        ruta: "/mis-proyectos",
        roles: [4],
        icono: "▣",
      },
      {
        nombre: "Mi equipo",
        ruta: "/mi-equipo",
        roles: [4],
        icono: "♧",
      },
      {
        nombre: "Mis tareas",
        ruta: "/mis-tareas",
        roles: [4],
        icono: "✓",
      },
      {
        nombre: "Mis habilidades",
        ruta: "/mis-habilidades",
        roles: [4],
        icono: "◆",
      },
      {
        nombre: "Proyectos",
        ruta: "/proyectos",
        roles: [1, 2, 3],
        icono: "▣",
      },
      {
        nombre: "Personas",
        ruta: "/personas",
        roles: [1, 2, 3],
        icono: "♙",
      },
      {
        nombre: "Equipos",
        ruta: "/equipos",
        roles: [1, 2, 3],
        icono: "♧",
      },
      {
        nombre: "Chat",
        ruta: "/chat",
        roles: [1, 2, 3, 4],
        icono: "💬",
      },
      {
        nombre: "Tareas",
        ruta: "/tareas",
        roles: [1, 2, 3],
        icono: "✓",
      },
      {
        nombre: "Habilidades",
        ruta: "/habilidades",
        roles: [1, 3],
        icono: "◆",
      },
    ],
  },
  {
    titulo: "PLATFORM",
    items: [
      {
        nombre: "Organizaciones",
        ruta: "/organizaciones",
        roles: [5],
        icono: "◎",
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
    case 5:
      return "Super Admin";
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
  const [fotoUrl, setFotoUrl] = useState("");

  useEffect(() => {
    if (!usuario?.id_persona) return;
    let objectUrl = "";
    blobFotoPersona(usuario.id_persona)
      .then((blob) => {
        objectUrl = URL.createObjectURL(blob);
        setFotoUrl(objectUrl);
      })
      .catch(() => setFotoUrl(""));
    return () => {
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [usuario?.id_persona]);

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
            <label className="sidebar-profile-avatar" title="Cambiar foto">
              {fotoUrl ? (
                <img src={fotoUrl} alt="Foto de perfil" />
              ) : (
                obtenerInicial(usuario.nombre_usuario)
              )}
              <input
                type="file"
                accept="image/png,image/jpeg,image/webp"
                hidden
                onChange={async (e) => {
                  const archivo = e.target.files?.[0];
                  if (!archivo) return;
                  await subirMiFoto(archivo);
                  window.location.reload();
                }}
              />
            </label>

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
