import { useCallback, useEffect, useState, type FormEvent } from "react";
import { useAuth } from "../../context/AuthContext";
import "./Organizaciones.css";

const API_URL = "http://127.0.0.1:8000";

interface AdminResumen {
  id_usuario: number;
  nombre_usuario: string;
  email: string;
  nombre: string | null;
  apellido: string | null;
  telefono: string | null;
}

interface OrganizacionItem {
  id_organizacion: number;
  nombre: string;
  descripcion: string | null;
  codigo: string | null;
  estado: boolean;
  fecha_creacion: string;
  admin: AdminResumen | null;
}

interface PersonaOrg {
  id_persona: number;
  nombre: string;
  apellido: string;
  email: string;
  estado: boolean;
}

type ModoAdmin = "existente" | "nuevo";

function Organizaciones() {
  const { token } = useAuth();

  const [organizaciones, setOrganizaciones] = useState<OrganizacionItem[]>([]);
  const [cargandoLista, setCargandoLista] = useState(true);
  const [errorLista, setErrorLista] = useState("");

  const [nombre, setNombre] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [errorOrg, setErrorOrg] = useState("");
  const [okOrg, setOkOrg] = useState("");
  const [cargandoOrg, setCargandoOrg] = useState(false);

  const [orgSeleccionada, setOrgSeleccionada] =
    useState<OrganizacionItem | null>(null);
  const [modalAbierto, setModalAbierto] = useState(false);
  const [modo, setModo] = useState<ModoAdmin>("existente");

  const [personas, setPersonas] = useState<PersonaOrg[]>([]);
  const [cargandoPersonas, setCargandoPersonas] = useState(false);
  const [idPersonaSel, setIdPersonaSel] = useState<number | "">("");
  const [contrasenaPromover, setContrasenaPromover] = useState("");

  const [adminNombre, setAdminNombre] = useState("");
  const [adminApellido, setAdminApellido] = useState("");
  const [adminEmail, setAdminEmail] = useState("");
  const [adminTelefono, setAdminTelefono] = useState("");
  const [adminContrasena, setAdminContrasena] = useState("");

  const [errorAdmin, setErrorAdmin] = useState("");
  const [okAdmin, setOkAdmin] = useState("");
  const [cargandoAdmin, setCargandoAdmin] = useState(false);

  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };

  const cargarOrganizaciones = useCallback(async () => {
    setCargandoLista(true);
    setErrorLista("");
    try {
      const res = await fetch(`${API_URL}/organizaciones`, { headers });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(
          data.detail || "No se pudieron cargar las organizaciones",
        );
      }
      const data: OrganizacionItem[] = await res.json();
      setOrganizaciones(data);
    } catch (err) {
      setErrorLista(err instanceof Error ? err.message : "Error al cargar");
    } finally {
      setCargandoLista(false);
    }
  }, [token]);

  useEffect(() => {
    cargarOrganizaciones();
  }, [cargarOrganizaciones]);

  const cargarPersonasOrg = async (idOrg: number) => {
    setCargandoPersonas(true);
    setPersonas([]);
    setIdPersonaSel("");
    try {
      const res = await fetch(`${API_URL}/organizaciones/${idOrg}/personas`, {
        headers,
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || "No se pudieron cargar personas");
      }
      const data: PersonaOrg[] = await res.json();
      setPersonas(data.filter((p) => p.estado !== false));
    } catch (err) {
      setErrorAdmin(
        err instanceof Error ? err.message : "Error al cargar personas",
      );
    } finally {
      setCargandoPersonas(false);
    }
  };

  const abrirModal = async (org: OrganizacionItem) => {
    setOrgSeleccionada(org);
    setModo(org.admin ? "existente" : "nuevo");
    setErrorAdmin("");
    setOkAdmin("");
    setAdminNombre("");
    setAdminApellido("");
    setAdminEmail("");
    setAdminTelefono("");
    setAdminContrasena("");
    setContrasenaPromover("");
    setModalAbierto(true);
    await cargarPersonasOrg(org.id_organizacion);
  };

  const cerrarModal = () => {
    if (cargandoAdmin) return;
    setModalAbierto(false);
    setOrgSeleccionada(null);
  };

  const crearOrganizacion = async (e: FormEvent) => {
    e.preventDefault();
    setErrorOrg("");
    setOkOrg("");
    setCargandoOrg(true);
    try {
      const res = await fetch(`${API_URL}/organizaciones`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          nombre: nombre.trim(),
          descripcion: descripcion.trim() || null,
        }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || "No se pudo crear la organización");
      }
      const data: OrganizacionItem = await res.json();
      setOkOrg(`Organización creada. Código: ${data.codigo ?? "—"}`);
      setNombre("");
      setDescripcion("");
      await cargarOrganizaciones();
      await abrirModal(data);
    } catch (err) {
      setErrorOrg(err instanceof Error ? err.message : "Error al crear");
    } finally {
      setCargandoOrg(false);
    }
  };

  const promoverAdmin = async (e: FormEvent) => {
    e.preventDefault();
    if (!orgSeleccionada || idPersonaSel === "") return;

    setErrorAdmin("");
    setOkAdmin("");

    if (orgSeleccionada.admin) {
      const ok = window.confirm(
        `¿Reemplazar al admin ${orgSeleccionada.admin.email}?`,
      );
      if (!ok) return;
    }

    setCargandoAdmin(true);
    try {
      const res = await fetch(
        `${API_URL}/organizaciones/${orgSeleccionada.id_organizacion}/admin/promover`,
        {
          method: "POST",
          headers,
          body: JSON.stringify({
            id_persona: Number(idPersonaSel),
            contrasena: contrasenaPromover.trim() || null,
          }),
        },
      );
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "No se pudo promover el admin",
        );
      }
      const data = await res.json();
      setOkAdmin(`Admin actualizado: ${data.email}`);
      await cargarOrganizaciones();
      setTimeout(cerrarModal, 1000);
    } catch (err) {
      setErrorAdmin(err instanceof Error ? err.message : "Error");
    } finally {
      setCargandoAdmin(false);
    }
  };

  const crearAdminNuevo = async (e: FormEvent) => {
    e.preventDefault();
    if (!orgSeleccionada) return;

    setErrorAdmin("");
    setOkAdmin("");

    if (orgSeleccionada.admin) {
      const ok = window.confirm(
        `¿Reemplazar al admin ${orgSeleccionada.admin.email}?`,
      );
      if (!ok) return;
    }

    setCargandoAdmin(true);
    try {
      const res = await fetch(
        `${API_URL}/organizaciones/${orgSeleccionada.id_organizacion}/admin`,
        {
          method: "POST",
          headers,
          body: JSON.stringify({
            nombre: adminNombre.trim(),
            apellido: adminApellido.trim(),
            email: adminEmail.trim(),
            telefono: adminTelefono.trim() || null,
            capacidad_horas_semana: 40,
            contrasena: adminContrasena,
          }),
        },
      );
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "No se pudo crear el admin",
        );
      }
      const data = await res.json();
      setOkAdmin(`Admin creado: ${data.email}`);
      await cargarOrganizaciones();
      setTimeout(cerrarModal, 1000);
    } catch (err) {
      setErrorAdmin(err instanceof Error ? err.message : "Error");
    } finally {
      setCargandoAdmin(false);
    }
  };

  const cambiarEstado = async (org: OrganizacionItem) => {
    const accion = org.estado ? "desactivar" : "activar";
    const ok = window.confirm(
      org.estado ? `¿Desactivar "${org.nombre}"?` : `¿Activar "${org.nombre}"?`,
    );
    if (!ok) return;
    try {
      const res = await fetch(
        `${API_URL}/organizaciones/${org.id_organizacion}/${accion}`,
        { method: "PATCH", headers },
      );
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || `No se pudo ${accion}`);
      }
      await cargarOrganizaciones();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Error");
    }
  };

  const total = organizaciones.length;
  const activas = organizaciones.filter((o) => o.estado).length;

  return (
    <div className="orgs-page">
      <div className="orgs-stats">
        <div className="orgs-stat">
          <span className="orgs-stat-value">{total}</span>
          <span className="orgs-stat-label">Organizaciones</span>
        </div>
        <div className="orgs-stat">
          <span className="orgs-stat-value">{activas}</span>
          <span className="orgs-stat-label">Activas</span>
        </div>
        <div className="orgs-stat">
          <span className="orgs-stat-value">{total - activas}</span>
          <span className="orgs-stat-label">Inactivas</span>
        </div>
      </div>

      <section className="orgs-card orgs-table-card">
        <div className="orgs-table-header">
          <h2>Organizaciones registradas</h2>
          <button
            type="button"
            className="orgs-refresh"
            onClick={cargarOrganizaciones}
          >
            Actualizar
          </button>
        </div>

        {cargandoLista && <p className="orgs-hint">Cargando...</p>}
        {errorLista && <div className="orgs-error">{errorLista}</div>}

        {!cargandoLista && !errorLista && (
          <div className="orgs-table-wrap">
            <table className="orgs-table">
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>Código</th>
                  <th>Estado</th>
                  <th>Admin</th>
                  <th>Contacto</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {organizaciones.length === 0 ? (
                  <tr>
                    <td colSpan={6}>No hay organizaciones registradas.</td>
                  </tr>
                ) : (
                  organizaciones.map((org) => (
                    <tr key={org.id_organizacion}>
                      <td>
                        <strong>{org.nombre}</strong>
                        {org.descripcion && (
                          <div className="orgs-desc">{org.descripcion}</div>
                        )}
                      </td>
                      <td>
                        <code>{org.codigo ?? "—"}</code>
                      </td>
                      <td>
                        <span
                          className={
                            org.estado
                              ? "orgs-badge activa"
                              : "orgs-badge inactiva"
                          }
                        >
                          {org.estado ? "Activa" : "Inactiva"}
                        </span>
                      </td>
                      <td>
                        {org.admin ? (
                          <>
                            {[org.admin.nombre, org.admin.apellido]
                              .filter(Boolean)
                              .join(" ") || org.admin.nombre_usuario}
                          </>
                        ) : (
                          <span className="orgs-muted">Sin admin</span>
                        )}
                      </td>
                      <td>
                        {org.admin ? (
                          <div className="orgs-contacto">
                            <span>{org.admin.email}</span>
                            {org.admin.telefono && (
                              <span>{org.admin.telefono}</span>
                            )}
                          </div>
                        ) : (
                          "—"
                        )}
                      </td>
                      <td>
                        <div className="orgs-actions">
                          <button
                            type="button"
                            className="orgs-btn-sm"
                            onClick={() => abrirModal(org)}
                          >
                            {org.admin ? "Cambiar admin" : "Asignar admin"}
                          </button>
                          <button
                            type="button"
                            className={
                              org.estado
                                ? "orgs-btn-sm danger"
                                : "orgs-btn-sm ok"
                            }
                            onClick={() => cambiarEstado(org)}
                            disabled={org.codigo === "FLOW-PLATFORM-0001"}
                          >
                            {org.estado ? "Desactivar" : "Activar"}
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="orgs-card" style={{ maxWidth: 480 }}>
        <h2>Nueva organización</h2>
        <p className="orgs-hint">Luego asignas el admin en el modal.</p>
        <form onSubmit={crearOrganizacion} className="orgs-form">
          <label>
            Nombre
            <input
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
              required
              minLength={2}
            />
          </label>
          <label>
            Descripción (opcional)
            <textarea
              value={descripcion}
              onChange={(e) => setDescripcion(e.target.value)}
              rows={3}
            />
          </label>
          {errorOrg && <div className="orgs-error">{errorOrg}</div>}
          {okOrg && <div className="orgs-ok">{okOrg}</div>}
          <button type="submit" disabled={cargandoOrg}>
            {cargandoOrg ? "Creando..." : "Crear organización"}
          </button>
        </form>
      </section>

      {modalAbierto && orgSeleccionada && (
        <div className="orgs-modal-overlay" onClick={cerrarModal}>
          <div
            className="orgs-modal"
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
          >
            <div className="orgs-modal-head">
              <div>
                <h3>
                  {orgSeleccionada.admin ? "Cambiar admin" : "Asignar admin"}
                </h3>
                <p className="orgs-hint" style={{ margin: "6px 0 0" }}>
                  {orgSeleccionada.nombre} · {orgSeleccionada.codigo}
                </p>
              </div>
              <button
                type="button"
                className="orgs-modal-close"
                onClick={cerrarModal}
                disabled={cargandoAdmin}
              >
                ✕
              </button>
            </div>

            {orgSeleccionada.admin && (
              <div className="orgs-modal-current">
                Admin actual:{" "}
                <strong>
                  {[
                    orgSeleccionada.admin.nombre,
                    orgSeleccionada.admin.apellido,
                  ]
                    .filter(Boolean)
                    .join(" ") || orgSeleccionada.admin.nombre_usuario}
                </strong>{" "}
                ({orgSeleccionada.admin.email})
              </div>
            )}

            <div className="orgs-tabs">
              <button
                type="button"
                className={modo === "existente" ? "active" : ""}
                onClick={() => setModo("existente")}
              >
                Persona existente
              </button>
              <button
                type="button"
                className={modo === "nuevo" ? "active" : ""}
                onClick={() => setModo("nuevo")}
              >
                Admin nuevo
              </button>
            </div>

            {modo === "existente" ? (
              <form onSubmit={promoverAdmin} className="orgs-form">
                <label>
                  Persona de la organización
                  {cargandoPersonas ? (
                    <span className="orgs-hint"> Cargando...</span>
                  ) : (
                    <select
                      required
                      value={idPersonaSel}
                      onChange={(e) =>
                        setIdPersonaSel(
                          e.target.value ? Number(e.target.value) : "",
                        )
                      }
                    >
                      <option value="">Selecciona...</option>
                      {personas.map((p) => (
                        <option key={p.id_persona} value={p.id_persona}>
                          {p.nombre} {p.apellido} — {p.email}
                        </option>
                      ))}
                    </select>
                  )}
                </label>
                <label>
                  Contraseña (obligatoria si aún no tiene cuenta)
                  <input
                    type="password"
                    minLength={8}
                    value={contrasenaPromover}
                    onChange={(e) => setContrasenaPromover(e.target.value)}
                    placeholder="Mín. 8 caracteres si es cuenta nueva"
                  />
                </label>
                {errorAdmin && <div className="orgs-error">{errorAdmin}</div>}
                {okAdmin && <div className="orgs-ok">{okAdmin}</div>}
                <div className="orgs-modal-actions">
                  <button
                    type="button"
                    className="orgs-btn-secondary"
                    onClick={cerrarModal}
                    disabled={cargandoAdmin}
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    disabled={cargandoAdmin || !idPersonaSel}
                  >
                    {cargandoAdmin ? "Guardando..." : "Promover a admin"}
                  </button>
                </div>
              </form>
            ) : (
              <form onSubmit={crearAdminNuevo} className="orgs-form">
                <label>
                  Nombre
                  <input
                    value={adminNombre}
                    onChange={(e) => setAdminNombre(e.target.value)}
                    required
                  />
                </label>
                <label>
                  Apellido
                  <input
                    value={adminApellido}
                    onChange={(e) => setAdminApellido(e.target.value)}
                    required
                  />
                </label>
                <label>
                  Email (debe ser nuevo en el sistema)
                  <input
                    type="email"
                    value={adminEmail}
                    onChange={(e) => setAdminEmail(e.target.value)}
                    required
                  />
                </label>
                <label>
                  Teléfono
                  <input
                    value={adminTelefono}
                    onChange={(e) => setAdminTelefono(e.target.value)}
                  />
                </label>
                <label>
                  Contraseña
                  <input
                    type="password"
                    value={adminContrasena}
                    onChange={(e) => setAdminContrasena(e.target.value)}
                    required
                    minLength={8}
                  />
                </label>
                {errorAdmin && <div className="orgs-error">{errorAdmin}</div>}
                {okAdmin && <div className="orgs-ok">{okAdmin}</div>}
                <div className="orgs-modal-actions">
                  <button
                    type="button"
                    className="orgs-btn-secondary"
                    onClick={cerrarModal}
                    disabled={cargandoAdmin}
                  >
                    Cancelar
                  </button>
                  <button type="submit" disabled={cargandoAdmin}>
                    {cargandoAdmin ? "Guardando..." : "Crear admin"}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default Organizaciones;
