import { useEffect, useMemo, useState } from "react";

import {
  activarUsuario,
  actualizarUsuario,
  crearUsuario,
  desactivarUsuario,
  obtenerPersonas,
  obtenerRoles,
  obtenerUsuarios,
} from "../../service/api";

import type { Usuario, UsuarioCreate } from "../../types/usuario";
import type { Persona } from "../../types/persona";
import type { Rol } from "../../types/rol";

import "./Usuarios.css";

const ROLES_ADMINISTRABLES = [2, 3, 4];

function obtenerNombreRol(idRol: number, roles: Rol[]): string {
  return roles.find((rol) => rol.id_rol === idRol)?.nombre ?? "Rol desconocido";
}

function obtenerNombrePersona(idPersona: number, personas: Persona[]): string {
  const persona = personas.find((item) => item.id_persona === idPersona);

  if (!persona) {
    return "Persona no encontrada";
  }

  return `${persona.nombre} ${persona.apellido}`;
}

function obtenerInicial(nombreUsuario: string): string {
  return nombreUsuario.charAt(0).toUpperCase();
}

function obtenerInicialPersona(nombre: string): string {
  return nombre.charAt(0).toUpperCase();
}

function obtenerClaseRol(idRol: number): string {
  switch (idRol) {
    case 1:
      return "rol-admin";
    case 2:
      return "rol-lider";
    case 3:
      return "rol-secretario";
    case 4:
      return "rol-empleado";
    default:
      return "";
  }
}

function obtenerDescripcionRol(idRol: number): string {
  switch (idRol) {
    case 2:
      return "Lidera y supervisa proyectos";
    case 3:
      return "Gestiona información y usuarios";
    case 4:
      return "Acceso como miembro de la organización";
    default:
      return "";
  }
}

function Usuarios() {
  const [usuarios, setUsuarios] = useState<Usuario[]>([]);
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [roles, setRoles] = useState<Rol[]>([]);

  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);

  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");

  const [busqueda, setBusqueda] = useState("");
  const [filtroEstado, setFiltroEstado] = useState("TODOS");

  const [mostrarModal, setMostrarModal] = useState(false);
  const [modoEdicion, setModoEdicion] = useState(false);

  const [usuarioSeleccionado, setUsuarioSeleccionado] =
    useState<Usuario | null>(null);

  const [mostrarContrasena, setMostrarContrasena] = useState(false);

  const [formulario, setFormulario] = useState<UsuarioCreate>({
    id_persona: 0,
    id_rol: 4,
    nombre_usuario: "",
    email: "",
    contrasena: "",
  });

  const cargarDatos = async () => {
    setCargando(true);
    setError("");

    try {
      const [usuariosData, personasData, rolesData] = await Promise.all([
        obtenerUsuarios(),
        obtenerPersonas(),
        obtenerRoles(),
      ]);

      setUsuarios(usuariosData);
      setPersonas(personasData);
      setRoles(rolesData);
    } catch (errorApi) {
      setError(
        errorApi instanceof Error
          ? errorApi.message
          : "No fue posible cargar la información.",
      );
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  const usuariosFiltrados = useMemo(() => {
    const texto = busqueda.trim().toLowerCase();

    return usuarios.filter((usuario) => {
      const coincideTexto =
        !texto ||
        usuario.nombre_usuario.toLowerCase().includes(texto) ||
        usuario.email.toLowerCase().includes(texto) ||
        obtenerNombrePersona(usuario.id_persona, personas)
          .toLowerCase()
          .includes(texto);

      const coincideEstado =
        filtroEstado === "TODOS" ||
        (filtroEstado === "ACTIVOS" && usuario.estado) ||
        (filtroEstado === "INACTIVOS" && !usuario.estado);

      return coincideTexto && coincideEstado;
    });
  }, [usuarios, personas, busqueda, filtroEstado]);

  const personasDisponibles = useMemo(() => {
    const personasConUsuario = new Set(
      usuarios
        .filter((usuario) => usuario.estado)
        .map((usuario) => usuario.id_persona),
    );

    return personas.filter(
      (persona) =>
        persona.estado && !personasConUsuario.has(persona.id_persona),
    );
  }, [personas, usuarios]);

  const totalUsuarios = usuarios.length;
  const usuariosActivos = usuarios.filter((usuario) => usuario.estado).length;
  const usuariosInactivos = usuarios.filter(
    (usuario) => !usuario.estado,
  ).length;

  const abrirCrear = () => {
    setModoEdicion(false);
    setUsuarioSeleccionado(null);
    setMostrarContrasena(false);

    setFormulario({
      id_persona: personasDisponibles[0]?.id_persona ?? 0,
      id_rol: 4,
      nombre_usuario: "",
      email: "",
      contrasena: "",
    });

    setError("");
    setMensaje("");
    setMostrarModal(true);
  };

  const abrirEditar = (usuario: Usuario) => {
    setModoEdicion(true);
    setUsuarioSeleccionado(usuario);
    setMostrarContrasena(false);

    setFormulario({
      id_persona: usuario.id_persona,
      id_rol: usuario.id_rol,
      nombre_usuario: usuario.nombre_usuario,
      email: usuario.email,
      contrasena: "",
    });

    setError("");
    setMensaje("");
    setMostrarModal(true);
  };

  const cerrarModal = () => {
    if (guardando) {
      return;
    }

    setMostrarModal(false);
    setUsuarioSeleccionado(null);
    setMostrarContrasena(false);
  };

  const manejarCambio = (
    campo: keyof UsuarioCreate,
    valor: string | number,
  ) => {
    setFormulario((actual) => ({
      ...actual,
      [campo]: valor,
    }));
  };

  const manejarGuardar = async (evento: React.FormEvent) => {
    evento.preventDefault();

    setError("");
    setMensaje("");

    if (!modoEdicion) {
      if (!formulario.id_persona) {
        setError("Debes seleccionar una persona.");
        return;
      }

      if (!formulario.nombre_usuario.trim()) {
        setError("Debes ingresar un nombre de usuario.");
        return;
      }

      if (!formulario.email.trim()) {
        setError("Debes ingresar un correo.");
        return;
      }

      if (formulario.contrasena.length < 8) {
        setError("La contraseña debe tener al menos 8 caracteres.");
        return;
      }
    }

    setGuardando(true);

    try {
      if (modoEdicion && usuarioSeleccionado) {
        await actualizarUsuario(usuarioSeleccionado.id_usuario, {
          id_rol: formulario.id_rol,
          nombre_usuario: formulario.nombre_usuario.trim(),
          email: formulario.email.trim(),
        });

        setMensaje("Usuario actualizado correctamente.");
      } else {
        await crearUsuario({
          id_persona: formulario.id_persona,
          id_rol: formulario.id_rol,
          nombre_usuario: formulario.nombre_usuario.trim(),
          email: formulario.email.trim(),
          contrasena: formulario.contrasena,
        });

        setMensaje("Usuario creado correctamente.");
      }

      await cargarDatos();
      setMostrarModal(false);
      setUsuarioSeleccionado(null);
    } catch (errorApi) {
      setError(
        errorApi instanceof Error
          ? errorApi.message
          : "No fue posible guardar el usuario.",
      );
    } finally {
      setGuardando(false);
    }
  };

  const manejarCambioEstado = async (usuario: Usuario) => {
    const accion = usuario.estado ? "desactivar" : "activar";

    const confirmado = window.confirm(
      `¿Seguro que deseas ${accion} a "${usuario.nombre_usuario}"?`,
    );

    if (!confirmado) {
      return;
    }

    setError("");
    setMensaje("");

    try {
      if (usuario.estado) {
        await desactivarUsuario(usuario.id_usuario);
        setMensaje("Usuario desactivado correctamente.");
      } else {
        await activarUsuario(usuario.id_usuario);
        setMensaje("Usuario activado correctamente.");
      }

      await cargarDatos();
    } catch (errorApi) {
      setError(
        errorApi instanceof Error
          ? errorApi.message
          : "No fue posible cambiar el estado del usuario.",
      );
    }
  };

  const cerrarMensajes = () => {
    setError("");
    setMensaje("");
  };

  return (
    <section className="usuarios-page">
      <div className="usuarios-header">
        <div className="usuarios-heading">
          <span className="usuarios-kicker">ADMINISTRACIÓN</span>

          <h1>Usuarios</h1>

          <p>Administra las cuentas, roles y accesos de tu organización.</p>
        </div>

        <button
          type="button"
          className="usuarios-primary-button"
          onClick={abrirCrear}
          disabled={personasDisponibles.length === 0}
        >
          <span className="button-plus">+</span>
          Nuevo usuario
        </button>
      </div>

      {(error || mensaje) && (
        <div
          className={`usuarios-alert ${
            error ? "usuarios-alert-error" : "usuarios-alert-success"
          }`}
        >
          <div className="alert-icon">{error ? "!" : "✓"}</div>

          <span>{error || mensaje}</span>

          <button
            type="button"
            onClick={cerrarMensajes}
            aria-label="Cerrar mensaje"
          >
            ×
          </button>
        </div>
      )}

      <div className="usuarios-summary">
        <div className="usuarios-summary-card summary-total">
          <div className="summary-card-top">
            <span>Total de usuarios</span>
            <div className="summary-icon">◉</div>
          </div>

          <strong>{totalUsuarios}</strong>

          <small>Cuentas registradas</small>
        </div>

        <div className="usuarios-summary-card summary-active">
          <div className="summary-card-top">
            <span>Usuarios activos</span>
            <div className="summary-icon">✓</div>
          </div>

          <strong>{usuariosActivos}</strong>

          <small>Con acceso habilitado</small>
        </div>

        <div className="usuarios-summary-card summary-inactive">
          <div className="summary-card-top">
            <span>Usuarios inactivos</span>
            <div className="summary-icon">○</div>
          </div>

          <strong>{usuariosInactivos}</strong>

          <small>Acceso actualmente deshabilitado</small>
        </div>
      </div>

      <div className="usuarios-toolbar">
        <div className="usuarios-toolbar-title">
          <span className="toolbar-dot" />
          <div>
            <strong>Directorio de usuarios</strong>
            <small>
              {usuariosFiltrados.length}{" "}
              {usuariosFiltrados.length === 1 ? "resultado" : "resultados"}
            </small>
          </div>
        </div>

        <div className="usuarios-filtros">
          <div className="usuarios-search">
            <span className="search-icon">⌕</span>

            <input
              type="text"
              placeholder="Buscar usuario, correo o persona..."
              value={busqueda}
              onChange={(evento) => setBusqueda(evento.target.value)}
            />

            {busqueda && (
              <button
                type="button"
                className="search-clear"
                onClick={() => setBusqueda("")}
                aria-label="Limpiar búsqueda"
              >
                ×
              </button>
            )}
          </div>

          <div className="usuarios-filter-wrapper">
            <span>Estado</span>

            <select
              className="usuarios-filter"
              value={filtroEstado}
              onChange={(evento) => setFiltroEstado(evento.target.value)}
            >
              <option value="TODOS">Todos</option>
              <option value="ACTIVOS">Activos</option>
              <option value="INACTIVOS">Inactivos</option>
            </select>
          </div>
        </div>
      </div>

      <div className="usuarios-table-container">
        {cargando ? (
          <div className="usuarios-loading">
            <div className="usuarios-spinner" />

            <strong>Cargando usuarios</strong>

            <p>Estamos preparando el directorio de tu organización.</p>
          </div>
        ) : usuariosFiltrados.length === 0 ? (
          <div className="usuarios-empty">
            <div className="usuarios-empty-icon">◎</div>

            <h3>No encontramos usuarios</h3>

            <p>
              {busqueda || filtroEstado !== "TODOS"
                ? "Prueba cambiando los filtros de búsqueda."
                : "Todavía no hay usuarios registrados."}
            </p>

            {!busqueda && filtroEstado === "TODOS" && (
              <button
                type="button"
                className="usuarios-empty-button"
                onClick={abrirCrear}
                disabled={personasDisponibles.length === 0}
              >
                + Crear primer usuario
              </button>
            )}
          </div>
        ) : (
          <div className="usuarios-table-wrapper">
            <table className="usuarios-table">
              <thead>
                <tr>
                  <th>Usuario</th>
                  <th>Persona</th>
                  <th>Rol</th>
                  <th>Correo</th>
                  <th>Estado</th>
                  <th>Último acceso</th>
                  <th>Acciones</th>
                </tr>
              </thead>

              <tbody>
                {usuariosFiltrados.map((usuario) => {
                  const persona = personas.find(
                    (item) => item.id_persona === usuario.id_persona,
                  );

                  return (
                    <tr
                      key={usuario.id_usuario}
                      className={!usuario.estado ? "usuario-row-inactive" : ""}
                    >
                      <td>
                        <div className="usuario-identidad">
                          <div
                            className={`usuario-avatar ${
                              !usuario.estado ? "avatar-inactive" : ""
                            }`}
                          >
                            {obtenerInicial(usuario.nombre_usuario)}
                          </div>

                          <div className="usuario-identidad-info">
                            <strong>{usuario.nombre_usuario}</strong>

                            <span>ID #{usuario.id_usuario}</span>
                          </div>
                        </div>
                      </td>

                      <td>
                        <div className="usuario-persona">
                          <div className="persona-mini-avatar">
                            {persona
                              ? obtenerInicialPersona(persona.nombre)
                              : "?"}
                          </div>

                          <div>
                            <strong>
                              {obtenerNombrePersona(
                                usuario.id_persona,
                                personas,
                              )}
                            </strong>

                            <span>Persona #{usuario.id_persona}</span>
                          </div>
                        </div>
                      </td>

                      <td>
                        <span
                          className={`usuario-role ${obtenerClaseRol(
                            usuario.id_rol,
                          )}`}
                        >
                          <span className="role-dot" />
                          {obtenerNombreRol(usuario.id_rol, roles)}
                        </span>
                      </td>

                      <td>
                        <span className="usuario-email">{usuario.email}</span>
                      </td>

                      <td>
                        <span
                          className={`usuario-status ${
                            usuario.estado
                              ? "usuario-status-active"
                              : "usuario-status-inactive"
                          }`}
                        >
                          <span />
                          {usuario.estado ? "Activo" : "Inactivo"}
                        </span>
                      </td>

                      <td>
                        <div className="usuario-access">
                          <strong>
                            {usuario.ultimo_acceso
                              ? new Date(
                                  usuario.ultimo_acceso,
                                ).toLocaleDateString("es-CO", {
                                  day: "2-digit",
                                  month: "2-digit",
                                  year: "2-digit",
                                })
                              : "Nunca"}
                          </strong>

                          {usuario.ultimo_acceso && (
                            <span>
                              {new Date(
                                usuario.ultimo_acceso,
                              ).toLocaleTimeString("es-CO", {
                                hour: "2-digit",
                                minute: "2-digit",
                              })}
                            </span>
                          )}
                        </div>
                      </td>

                      <td>
                        <div className="usuario-actions">
                          <button
                            type="button"
                            className="usuario-action-edit"
                            onClick={() => abrirEditar(usuario)}
                          >
                            <span>✎</span>
                            Editar
                          </button>

                          {usuario.id_rol !== 1 && (
                            <button
                              type="button"
                              className={
                                usuario.estado
                                  ? "usuario-action-disable"
                                  : "usuario-action-enable"
                              }
                              onClick={() => manejarCambioEstado(usuario)}
                            >
                              {usuario.estado ? "Desactivar" : "Activar"}
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {mostrarModal && (
        <div
          className="usuarios-modal-overlay"
          onMouseDown={(evento) => {
            if (evento.target === evento.currentTarget) {
              cerrarModal();
            }
          }}
        >
          <div
            className="usuarios-modal"
            onMouseDown={(evento) => evento.stopPropagation()}
          >
            <div className="usuarios-modal-top">
              <div className="modal-brand">
                <div className="modal-brand-icon">
                  {modoEdicion ? "✎" : "+"}
                </div>

                <div>
                  <span>
                    {modoEdicion ? "GESTIÓN DE CUENTA" : "NUEVA CUENTA"}
                  </span>

                  <h2>{modoEdicion ? "Editar usuario" : "Crear usuario"}</h2>
                </div>
              </div>

              <button
                type="button"
                className="usuarios-modal-close"
                onClick={cerrarModal}
                disabled={guardando}
                aria-label="Cerrar"
              >
                ×
              </button>
            </div>

            <div className="modal-description">
              {modoEdicion
                ? "Actualiza los datos y permisos de esta cuenta."
                : "Crea una cuenta de acceso para un miembro de tu organización."}
            </div>

            <form className="usuarios-form" onSubmit={manejarGuardar}>
              {!modoEdicion && (
                <div className="usuarios-form-group">
                  <label htmlFor="usuario-persona">Persona</label>

                  <select
                    id="usuario-persona"
                    value={formulario.id_persona}
                    onChange={(evento) =>
                      manejarCambio("id_persona", Number(evento.target.value))
                    }
                    disabled={guardando}
                    required
                  >
                    <option value={0}>Selecciona una persona</option>

                    {personasDisponibles.map((persona) => (
                      <option
                        key={persona.id_persona}
                        value={persona.id_persona}
                      >
                        {persona.nombre} {persona.apellido}
                      </option>
                    ))}
                  </select>

                  {formulario.id_persona > 0 && (
                    <div className="selected-person">
                      <div className="selected-person-avatar">
                        {obtenerInicialPersona(
                          personas.find(
                            (persona) =>
                              persona.id_persona === formulario.id_persona,
                          )?.nombre ?? "U",
                        )}
                      </div>

                      <div>
                        <strong>
                          {obtenerNombrePersona(
                            formulario.id_persona,
                            personas,
                          )}
                        </strong>

                        <span>Persona seleccionada</span>
                      </div>
                    </div>
                  )}
                </div>
              )}

              <div className="form-row">
                <div className="usuarios-form-group">
                  <label htmlFor="usuario-nombre">Nombre de usuario</label>

                  <input
                    id="usuario-nombre"
                    type="text"
                    minLength={3}
                    maxLength={100}
                    value={formulario.nombre_usuario}
                    onChange={(evento) =>
                      manejarCambio("nombre_usuario", evento.target.value)
                    }
                    disabled={guardando}
                    placeholder="Ej. einer.quiroz"
                    required
                  />
                </div>

                <div className="usuarios-form-group">
                  <label htmlFor="usuario-rol">Rol de acceso</label>

                  <select
                    id="usuario-rol"
                    value={formulario.id_rol}
                    onChange={(evento) =>
                      manejarCambio("id_rol", Number(evento.target.value))
                    }
                    disabled={guardando}
                    required
                  >
                    {roles
                      .filter((rol) =>
                        ROLES_ADMINISTRABLES.includes(rol.id_rol),
                      )
                      .map((rol) => (
                        <option key={rol.id_rol} value={rol.id_rol}>
                          {rol.nombre}
                        </option>
                      ))}
                  </select>

                  <small>{obtenerDescripcionRol(formulario.id_rol)}</small>
                </div>
              </div>

              <div className="usuarios-form-group">
                <label htmlFor="usuario-email">Correo electrónico</label>

                <div className="input-with-icon">
                  <span>@</span>

                  <input
                    id="usuario-email"
                    type="email"
                    value={formulario.email}
                    onChange={(evento) =>
                      manejarCambio("email", evento.target.value)
                    }
                    disabled={guardando}
                    placeholder="correo@ejemplo.com"
                    required
                  />
                </div>
              </div>

              {!modoEdicion && (
                <div className="usuarios-form-group">
                  <label htmlFor="usuario-contrasena">Contraseña</label>

                  <div className="input-with-action">
                    <input
                      id="usuario-contrasena"
                      type={mostrarContrasena ? "text" : "password"}
                      minLength={8}
                      maxLength={128}
                      value={formulario.contrasena}
                      onChange={(evento) =>
                        manejarCambio("contrasena", evento.target.value)
                      }
                      disabled={guardando}
                      placeholder="Mínimo 8 caracteres"
                      required
                    />

                    <button
                      type="button"
                      onClick={() => setMostrarContrasena((actual) => !actual)}
                      disabled={guardando}
                    >
                      {mostrarContrasena ? "Ocultar" : "Ver"}
                    </button>
                  </div>

                  <small>
                    La contraseña se almacena protegida en el backend.
                  </small>
                </div>
              )}

              {error && (
                <div className="usuarios-form-error">
                  <span>!</span>
                  {error}
                </div>
              )}

              <div className="usuarios-modal-actions">
                <button
                  type="button"
                  className="usuarios-secondary-button"
                  onClick={cerrarModal}
                  disabled={guardando}
                >
                  Cancelar
                </button>

                <button
                  type="submit"
                  className="usuarios-primary-button modal-submit"
                  disabled={guardando}
                >
                  {guardando
                    ? "Guardando..."
                    : modoEdicion
                      ? "Guardar cambios"
                      : "Crear usuario"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </section>
  );
}

export default Usuarios;
