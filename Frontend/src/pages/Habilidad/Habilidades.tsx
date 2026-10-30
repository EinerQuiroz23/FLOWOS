import { useEffect, useMemo, useState, type FormEvent } from "react";

import { obtenerHabilidades } from "../../service/api";
import { useAuth } from "../../context/AuthContext";
import { ROLES } from "../../utils/roles";

import "./Habilidades.css";

type Habilidad = {
  id_habilidad: number;
  nombre: string;
  descripcion?: string | null;
  estado?: boolean | null;
};

const API = "http://127.0.0.1:8000";
const POR_PAGINA = 8;

async function crearHabilidad(nombre: string): Promise<Habilidad> {
  const token = localStorage.getItem("flowos_token");
  const respuesta = await fetch(`${API}/habilidades/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ nombre }),
  });
  if (!respuesta.ok) {
    const error = await respuesta.json().catch(() => null);
    const detalle = error?.detail;
    const mensaje = Array.isArray(detalle)
      ? detalle.map((item: { msg?: string }) => item.msg || "").join(", ")
      : detalle || "No se pudo crear la habilidad";
    throw new Error(
      typeof mensaje === "string" ? mensaje : "No se pudo crear la habilidad",
    );
  }
  return respuesta.json();
}

function Habilidades() {
  const { usuario } = useAuth();
  const puedeCrear =
    usuario?.id_rol === ROLES.ADMIN || usuario?.id_rol === ROLES.SECRETARIO;

  const [habilidades, setHabilidades] = useState<Habilidad[]>([]);
  const [busqueda, setBusqueda] = useState("");
  const [pagina, setPagina] = useState(1);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  const [abierto, setAbierto] = useState(false);
  const [nombre, setNombre] = useState("");
  const [guardando, setGuardando] = useState(false);
  const [errorForm, setErrorForm] = useState("");

  const cargar = async () => {
    const datos = await obtenerHabilidades();
    setHabilidades(
      [...datos].sort((a, b) => a.nombre.localeCompare(b.nombre, "es")),
    );
  };

  useEffect(() => {
    cargar()
      .catch((err) =>
        setError(
          err instanceof Error
            ? err.message
            : "No se pudieron cargar las habilidades",
        ),
      )
      .finally(() => setCargando(false));
  }, []);

  const filtradas = useMemo(() => {
    const texto = busqueda.trim().toLowerCase();
    if (!texto) return habilidades;
    return habilidades.filter((h) => h.nombre.toLowerCase().includes(texto));
  }, [habilidades, busqueda]);

  const totalPaginas = Math.max(1, Math.ceil(filtradas.length / POR_PAGINA));
  const paginaSegura = Math.min(pagina, totalPaginas);
  const inicio = (paginaSegura - 1) * POR_PAGINA;
  const visibles = filtradas.slice(inicio, inicio + POR_PAGINA);

  const guardar = async (e: FormEvent) => {
    e.preventDefault();
    if (!nombre.trim()) return;
    setGuardando(true);
    setErrorForm("");
    try {
      await crearHabilidad(nombre.trim());
      await cargar();
      setNombre("");
      setAbierto(false);
      setBusqueda("");
      setPagina(1);
    } catch (err) {
      setErrorForm(
        err instanceof Error ? err.message : "No se pudo crear la habilidad",
      );
    } finally {
      setGuardando(false);
    }
  };

  if (cargando) return <div className="hab-msg">Cargando habilidades...</div>;
  if (error) return <div className="hab-error">{error}</div>;

  return (
    <section className="hab-page">
      <header className="hab-head">
        <div>
          <span>CATÁLOGO</span>
          <h1>Habilidades</h1>
          <p>Estas son las que luego pides en una tarea y OPTIMA compara.</p>
        </div>
        <div className="hab-head-side">
          <strong>{filtradas.length}</strong>
          <span>{busqueda ? "encontradas" : "en el catálogo"}</span>
          {puedeCrear && (
            <button
              type="button"
              className="hab-btn"
              onClick={() => setAbierto(true)}
            >
              + Nueva habilidad
            </button>
          )}
        </div>
      </header>

      <div className="hab-toolbar">
        <label>
          Buscar
          <input
            value={busqueda}
            placeholder="Nombre de la habilidad"
            onChange={(e) => {
              setBusqueda(e.target.value);
              setPagina(1);
            }}
          />
        </label>
      </div>

      {visibles.length === 0 ? (
        <p className="hab-msg">No hay habilidades con esa búsqueda.</p>
      ) : (
        <div className="hab-table">
          <div className="hab-row hab-row-head">
            <span>#</span>
            <span>Nombre</span>
            <span>Estado</span>
          </div>
          {visibles.map((h, indice) => (
            <div className="hab-row" key={h.id_habilidad}>
              <span>{inicio + indice + 1}</span>
              <strong>{h.nombre}</strong>
              <span className={h.estado === false ? "hab-off" : "hab-on"}>
                {h.estado === false ? "Inactiva" : "Activa"}
              </span>
            </div>
          ))}
        </div>
      )}

      <div className="hab-pager">
        <span>
          {filtradas.length === 0
            ? "0 habilidades"
            : `${inicio + 1}–${Math.min(inicio + POR_PAGINA, filtradas.length)} de ${filtradas.length}`}
        </span>
        <div>
          <button
            type="button"
            disabled={paginaSegura <= 1}
            onClick={() => setPagina((p) => Math.max(1, p - 1))}
          >
            Anterior
          </button>
          {Array.from({ length: totalPaginas }, (_, i) => i + 1).map((n) => (
            <button
              key={n}
              type="button"
              className={n === paginaSegura ? "active" : ""}
              onClick={() => setPagina(n)}
            >
              {n}
            </button>
          ))}
          <button
            type="button"
            disabled={paginaSegura >= totalPaginas}
            onClick={() => setPagina((p) => p + 1)}
          >
            Siguiente
          </button>
        </div>
      </div>

      {abierto && (
        <div
          className="hab-modal"
          onClick={() => !guardando && setAbierto(false)}
        >
          <form
            className="hab-form"
            onClick={(e) => e.stopPropagation()}
            onSubmit={guardar}
          >
            <div className="hab-form-head">
              <div>
                <span>NUEVA</span>
                <h2>Crear habilidad</h2>
              </div>
              <button
                type="button"
                onClick={() => setAbierto(false)}
                disabled={guardando}
              >
                ×
              </button>
            </div>
            <label>
              Nombre
              <input
                required
                autoFocus
                value={nombre}
                placeholder="Ej. React, SQL, Liderazgo"
                onChange={(e) => setNombre(e.target.value)}
              />
            </label>
            {errorForm && <p className="hab-error">{errorForm}</p>}
            <div className="hab-form-actions">
              <button
                type="button"
                className="hab-btn-ghost"
                onClick={() => setAbierto(false)}
                disabled={guardando}
              >
                Cancelar
              </button>
              <button type="submit" className="hab-btn" disabled={guardando}>
                {guardando ? "Guardando..." : "Crear habilidad"}
              </button>
            </div>
          </form>
        </div>
      )}
    </section>
  );
}

export default Habilidades;
