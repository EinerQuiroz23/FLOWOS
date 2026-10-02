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

function Organizaciones() {
  const { token } = useAuth();

  const [organizaciones, setOrganizaciones] = useState<OrganizacionItem[]>([]);
  const [cargandoLista, setCargandoLista] = useState(true);
  const [errorLista, setErrorLista] = useState("");

  // Crear org
  const [nombre, setNombre] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [errorOrg, setErrorOrg] = useState("");
  const [okOrg, setOkOrg] = useState("");
  const [cargandoOrg, setCargandoOrg] = useState(false);
  const [orgSeleccionada, setOrgSeleccionada] =
    useState<OrganizacionItem | null>(null);

  // Crear admin
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
      setOrgSeleccionada(data);
      await cargarOrganizaciones();
    } catch (err) {
      setErrorOrg(err instanceof Error ? err.message : "Error al crear");
    } finally {
      setCargandoOrg(false);
    }
  };

  const crearAdmin = async (e: FormEvent) => {
    e.preventDefault();
    setErrorAdmin("");
    setOkAdmin("");

    if (!orgSeleccionada) {
      setErrorAdmin("Selecciona o crea una organización primero.");
      return;
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
      setAdminNombre("");
      setAdminApellido("");
      setAdminEmail("");
      setAdminTelefono("");
      setAdminContrasena("");
      await cargarOrganizaciones();
    } catch (err) {
      setErrorAdmin(
        err instanceof Error ? err.message : "Error al crear admin",
      );
    } finally {
      setCargandoAdmin(false);
    }
  };

  const cambiarEstado = async (org: OrganizacionItem) => {
    const accion = org.estado ? "desactivar" : "activar";
    const ok = window.confirm(
      org.estado
        ? `¿Desactivar "${org.nombre}"? Los usuarios de esa organización no podrán entrar.`
        : `¿Activar "${org.nombre}"?`,
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
      {/* RESUMEN */}
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

      {/* TABLA */}
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
                            onClick={() => setOrgSeleccionada(org)}
                          >
                            Usar
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

      <div className="orgs-grid">
        {/* CREAR ORG */}
        <section className="orgs-card">
          <h2>Nueva organización</h2>
          <p className="orgs-hint">
            Se genera un código único automáticamente.
          </p>

          <form onSubmit={crearOrganizacion} className="orgs-form">
            <label>
              Nombre
              <input
                value={nombre}
                onChange={(e) => setNombre(e.target.value)}
                required
                minLength={2}
                placeholder="Empresa Ejemplo S.A."
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

        {/* CREAR ADMIN */}
        <section className="orgs-card">
          <h2>Admin de la organización</h2>
          <p className="orgs-hint">
            {orgSeleccionada
              ? `Org seleccionada: ${orgSeleccionada.nombre} · ${orgSeleccionada.codigo}`
              : "Crea una org o pulsa «Usar» en la tabla."}
          </p>

          <form onSubmit={crearAdmin} className="orgs-form">
            <label>
              Nombre
              <input
                value={adminNombre}
                onChange={(e) => setAdminNombre(e.target.value)}
                required
                disabled={!orgSeleccionada}
              />
            </label>
            <label>
              Apellido
              <input
                value={adminApellido}
                onChange={(e) => setAdminApellido(e.target.value)}
                required
                disabled={!orgSeleccionada}
              />
            </label>
            <label>
              Email
              <input
                type="email"
                value={adminEmail}
                onChange={(e) => setAdminEmail(e.target.value)}
                required
                disabled={!orgSeleccionada}
              />
            </label>
            <label>
              Teléfono
              <input
                value={adminTelefono}
                onChange={(e) => setAdminTelefono(e.target.value)}
                disabled={!orgSeleccionada}
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
                disabled={!orgSeleccionada}
              />
            </label>
            {errorAdmin && <div className="orgs-error">{errorAdmin}</div>}
            {okAdmin && <div className="orgs-ok">{okAdmin}</div>}
            <button type="submit" disabled={!orgSeleccionada || cargandoAdmin}>
              {cargandoAdmin ? "Creando..." : "Crear admin"}
            </button>
          </form>
        </section>
      </div>
    </div>
  );
}

export default Organizaciones;
