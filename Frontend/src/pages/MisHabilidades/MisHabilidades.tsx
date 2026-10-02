import { useEffect, useState, type FormEvent } from "react";
import {
  obtenerMisHabilidades,
  obtenerHabilidades,
  obtenerNivelesHabilidad,
  crearMiHabilidad,
  type PersonaHabilidad,
  type Habilidad,
  type NivelHabilidad,
} from "../../service/api";
import { useAuth } from "../../context/AuthContext";
import "./MisHabilidades.css";

function MisHabilidades() {
  const { usuario } = useAuth();

  const [misHabilidades, setMisHabilidades] = useState<PersonaHabilidad[]>([]);
  const [catalogoHabilidades, setCatalogoHabilidades] = useState<Habilidad[]>(
    [],
  );
  const [catalogoNiveles, setCatalogoNiveles] = useState<NivelHabilidad[]>([]);
  const [idHabilidad, setIdHabilidad] = useState("");
  const [idNivel, setIdNivel] = useState("");
  const [anios, setAnios] = useState("1");
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");
  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);

  const cargar = async () => {
    const [mias, habs, niveles] = await Promise.all([
      obtenerMisHabilidades(),
      obtenerHabilidades(),
      obtenerNivelesHabilidad(),
    ]);
    setMisHabilidades(mias);
    setCatalogoHabilidades(habs.filter((h) => h.estado !== false));
    setCatalogoNiveles(niveles);
  };

  useEffect(() => {
    cargar()
      .catch((e) => setErr(e instanceof Error ? e.message : "Error"))
      .finally(() => setCargando(false));
  }, []);

  const guardar = async (e: FormEvent) => {
    e.preventDefault();
    setMsg("");
    setErr("");
    if (!usuario?.id_persona) {
      setErr("No se identificó tu persona.");
      return;
    }
    setGuardando(true);
    try {
      await crearMiHabilidad({
        id_persona: usuario.id_persona,
        id_habilidad: Number(idHabilidad),
        id_nivel: Number(idNivel),
        años_experiencia: Number(anios),
      });
      setMsg("Habilidad registrada.");
      setIdHabilidad("");
      setIdNivel("");
      setAnios("1");
      await cargar();
    } catch (error) {
      setErr(error instanceof Error ? error.message : "No se pudo guardar");
    } finally {
      setGuardando(false);
    }
  };

  const nombreHab = (id: number) =>
    catalogoHabilidades.find((h) => h.id_habilidad === id)?.nombre ?? `#${id}`;
  const nombreNiv = (id: number) =>
    catalogoNiveles.find((n) => n.id_nivel === id)?.nombre ?? `#${id}`;

  if (cargando) {
    return <div className="mis-hab-msg">Cargando habilidades...</div>;
  }

  return (
    <div className="mis-hab-page">
      <section className="mis-hab-card">
        <h2>Mis habilidades</h2>
        <p className="mis-hab-hint">
          OPTIMA usa este perfil para proponerte en tareas y equipos.
        </p>

        {misHabilidades.length === 0 ? (
          <p className="mis-hab-hint">Aún no tienes habilidades registradas.</p>
        ) : (
          <ul className="mis-hab-list">
            {misHabilidades.map((h) => (
              <li key={h.id_persona_habilidad}>
                <strong>{nombreHab(h.id_habilidad)}</strong>
                <span>
                  {nombreNiv(h.id_nivel)} · {h.años_experiencia} año(s)
                </span>
              </li>
            ))}
          </ul>
        )}

        <h3>Agregar habilidad</h3>
        <form onSubmit={guardar} className="mis-hab-form">
          <label>
            Habilidad
            <select
              value={idHabilidad}
              onChange={(e) => setIdHabilidad(e.target.value)}
              required
            >
              <option value="">Selecciona</option>
              {catalogoHabilidades.map((h) => (
                <option key={h.id_habilidad} value={h.id_habilidad}>
                  {h.nombre}
                </option>
              ))}
            </select>
          </label>
          <label>
            Nivel
            <select
              value={idNivel}
              onChange={(e) => setIdNivel(e.target.value)}
              required
            >
              <option value="">Selecciona</option>
              {catalogoNiveles.map((n) => (
                <option key={n.id_nivel} value={n.id_nivel}>
                  {n.nombre}
                </option>
              ))}
            </select>
          </label>
          <label>
            Años
            <input
              type="number"
              min={0}
              max={50}
              step={0.5}
              value={anios}
              onChange={(e) => setAnios(e.target.value)}
              required
            />
          </label>
          <button type="submit" disabled={guardando}>
            {guardando ? "Guardando..." : "Agregar"}
          </button>
        </form>
        {msg && <div className="mis-hab-ok">{msg}</div>}
        {err && <div className="mis-hab-error">{err}</div>}
      </section>
    </div>
  );
}

export default MisHabilidades;
