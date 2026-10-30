import { useEffect, useState, type FormEvent } from "react";

import { obtenerProyectos } from "../../service/api";
import { useAuth } from "../../context/AuthContext";
import { ROLES } from "../../utils/roles";
import type { Proyecto } from "../../types/proyecto";

import "./Proyectos.css";

const API = "http://127.0.0.1:8000";

type FormProyecto = {
  nombre: string;
  descripcion: string;
  fecha_inicio: string;
  fecha_limite: string;
};

const formVacio: FormProyecto = {
  nombre: "",
  descripcion: "",
  fecha_inicio: "",
  fecha_limite: "",
};

async function api<T>(ruta: string, opciones?: RequestInit): Promise<T> {
  const token = localStorage.getItem("flowos_token");
  const respuesta = await fetch(`${API}${ruta}`, {
    ...opciones,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
  if (!respuesta.ok) {
    const error = await respuesta.json().catch(() => null);
    const detalle = error?.detail;
    const mensaje = Array.isArray(detalle)
      ? detalle.map((item: { msg?: string }) => item.msg || "").join(", ")
      : detalle || "No se pudo guardar el proyecto";
    throw new Error(mensaje);
  }
  return respuesta.json();
}

function etiquetaEstado(estado: string): string {
  const mapa: Record<string, string> = {
    PLANIFICACION: "Planificación",
    ACTIVO: "Activo",
    PAUSADO: "Pausado",
    FINALIZADO: "Finalizado",
    CANCELADO: "Cancelado",
  };
  return mapa[estado] || estado;
}

function Proyectos() {
  const { usuario } = useAuth();
  const puedeGestionar =
    usuario?.id_rol === ROLES.ADMIN ||
    usuario?.id_rol === ROLES.SECRETARIO ||
    usuario?.id_rol === ROLES.LIDER_PROYECTO;

  const [proyectos, setProyectos] = useState<Proyecto[]>([]);
  const [elegido, setElegido] = useState<Proyecto | null>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [aviso, setAviso] = useState("");
  const [mostrarForm, setMostrarForm] = useState(false);
  const [form, setForm] = useState<FormProyecto>(formVacio);
  const [guardando, setGuardando] = useState(false);
  const [cambiando, setCambiando] = useState(false);

  const cargar = async () => {
    const datos = await obtenerProyectos();
    setProyectos(datos);
    setElegido((actual) =>
      actual
        ? datos.find((item) => item.id_proyecto === actual.id_proyecto) ||
          datos[0] ||
          null
        : datos[0] || null,
    );
  };

  useEffect(() => {
    cargar()
      .catch((err) =>
        setError(
          err instanceof Error
            ? err.message
            : "No se pudieron cargar los proyectos",
        ),
      )
      .finally(() => setCargando(false));
  }, []);

  const crear = async (event: FormEvent) => {
    event.preventDefault();
    try {
      setGuardando(true);
      setError("");
      const nuevo = await api<Proyecto>("/proyectos/", {
        method: "POST",
        body: JSON.stringify({
          nombre: form.nombre.trim(),
          descripcion: form.descripcion.trim() || null,
          fecha_inicio: form.fecha_inicio,
          fecha_limite: form.fecha_limite,
        }),
      });
      await api(`/proyectos/${nuevo.id_proyecto}/estado?nuevo_estado=ACTIVO`, {
        method: "PATCH",
      });
      await cargar();
      setMostrarForm(false);
      setForm(formVacio);
      setAviso(`"${nuevo.nombre}" quedó creado y activo.`);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "No se pudo crear el proyecto",
      );
    } finally {
      setGuardando(false);
    }
  };

  const cambiarEstado = async (estado: "ACTIVO" | "PAUSADO") => {
    if (!elegido) return;
    try {
      setCambiando(true);
      setError("");
      await api(
        `/proyectos/${elegido.id_proyecto}/estado?nuevo_estado=${estado}`,
        { method: "PATCH" },
      );
      await cargar();
      setAviso(
        estado === "ACTIVO"
          ? `"${elegido.nombre}" quedó activo.`
          : `"${elegido.nombre}" quedó pausado.`,
      );
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "No se pudo cambiar el estado",
      );
    } finally {
      setCambiando(false);
    }
  };

  if (cargando) return <p className="proy-msg">Cargando proyectos...</p>;

  return (
    <section className="proy-page">
      <header className="proy-head">
        <div>
          <span>PROYECTOS</span>
          <h1>Proyectos de la organización</h1>
          <p>Crea el proyecto, déjalo activo y después arma sus tareas.</p>
        </div>
        {puedeGestionar && (
          <button
            type="button"
            className="proy-btn"
            onClick={() => setMostrarForm(true)}
          >
            Nuevo proyecto
          </button>
        )}
      </header>

      {error && <p className="proy-error">{error}</p>}
      {aviso && <p className="proy-ok">{aviso}</p>}

      <div className="proy-layout">
        <div className="proy-lista">
          {proyectos.length === 0 && (
            <p className="proy-msg">Todavía no hay proyectos.</p>
          )}
          {proyectos.map((proyecto) => (
            <button
              key={proyecto.id_proyecto}
              type="button"
              className={
                elegido?.id_proyecto === proyecto.id_proyecto
                  ? "proy-card active"
                  : "proy-card"
              }
              onClick={() => setElegido(proyecto)}
            >
              <span className={`proy-estado ${proyecto.estado.toLowerCase()}`}>
                {etiquetaEstado(proyecto.estado)}
              </span>
              <strong>{proyecto.nombre}</strong>
              <small>
                {proyecto.fecha_inicio} → {proyecto.fecha_limite}
              </small>
            </button>
          ))}
        </div>

        <article className="proy-detalle">
          {!elegido ? (
            <p className="proy-msg">Elige un proyecto.</p>
          ) : (
            <>
              <span className={`proy-estado ${elegido.estado.toLowerCase()}`}>
                {etiquetaEstado(elegido.estado)}
              </span>
              <h2>{elegido.nombre}</h2>
              <p>{elegido.descripcion || "Sin descripción."}</p>
              <div className="proy-fechas">
                <div>
                  <span>Inicio</span>
                  <strong>{elegido.fecha_inicio}</strong>
                </div>
                <div>
                  <span>Límite</span>
                  <strong>{elegido.fecha_limite}</strong>
                </div>
              </div>
              {puedeGestionar && (
                <div className="proy-actions">
                  {elegido.estado !== "ACTIVO" && (
                    <button
                      type="button"
                      className="proy-btn"
                      disabled={cambiando}
                      onClick={() => cambiarEstado("ACTIVO")}
                    >
                      Activar
                    </button>
                  )}
                  {elegido.estado === "ACTIVO" && (
                    <button
                      type="button"
                      className="proy-btn-ghost"
                      disabled={cambiando}
                      onClick={() => cambiarEstado("PAUSADO")}
                    >
                      Pausar
                    </button>
                  )}
                </div>
              )}
            </>
          )}
        </article>
      </div>

      {mostrarForm && (
        <div className="proy-modal">
          <form className="proy-form" onSubmit={crear}>
            <div className="proy-form-head">
              <div>
                <span>NUEVO PROYECTO</span>
                <h2>Nombre y descripción</h2>
              </div>
              <button type="button" onClick={() => setMostrarForm(false)}>
                ×
              </button>
            </div>
            <label>
              Nombre
              <input
                required
                value={form.nombre}
                onChange={(e) =>
                  setForm((f) => ({ ...f, nombre: e.target.value }))
                }
              />
            </label>
            <label>
              Descripción
              <textarea
                required
                rows={3}
                value={form.descripcion}
                onChange={(e) =>
                  setForm((f) => ({ ...f, descripcion: e.target.value }))
                }
              />
            </label>
            <div className="proy-fechas">
              <label>
                Inicio
                <input
                  required
                  type="date"
                  value={form.fecha_inicio}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, fecha_inicio: e.target.value }))
                  }
                />
              </label>
              <label>
                Límite
                <input
                  required
                  type="date"
                  value={form.fecha_limite}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, fecha_limite: e.target.value }))
                  }
                />
              </label>
            </div>
            <div className="proy-actions">
              <button
                type="button"
                className="proy-btn-ghost"
                onClick={() => setMostrarForm(false)}
              >
                Cancelar
              </button>
              <button type="submit" className="proy-btn" disabled={guardando}>
                {guardando ? "Guardando..." : "Crear y activar"}
              </button>
            </div>
          </form>
        </div>
      )}
    </section>
  );
}

export default Proyectos;
