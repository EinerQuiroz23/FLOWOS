import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type FormEvent,
} from "react";
import {
  obtenerMisEquiposPersona,
  obtenerEquipos,
  obtenerProyectos,
  obtenerPersonas,
  obtenerPersonasPorEquipo,
  obtenerMensajesBandeja,
  enviarMensajeEquipo,
  enviarArchivoChat,
  blobArchivoChat,
  blobFotoPersona,
  type EquipoPersonaItem,
  type MensajeChat,
} from "../../service/api";
import { useAuth } from "../../context/AuthContext";
import type { Equipo } from "../../types/equipo";
import type { Proyecto } from "../../types/proyecto";
import type { Persona } from "../../types/persona";
import "./MiEquipo.css";

interface EquipoDetalle {
  id_equipo: number;
  nombre: string;
  id_proyecto: number;
  nombre_proyecto: string;
  miRol: string;
  miDedicacion: number;
  integrantes: {
    id_persona: number;
    nombre: string;
    rol_equipo: string;
    dedicacion: number;
  }[];
}

function inicialNombre(nombre: string): string {
  const partes = nombre.trim().split(/\s+/);
  if (partes.length >= 2) return (partes[0][0] + partes[1][0]).toUpperCase();
  return (nombre[0] || "?").toUpperCase();
}

function esLider(rol?: string | null): boolean {
  return (rol || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toUpperCase()
    .includes("LIDER");
}

function textoRol(rol?: string | null): string {
  return esLider(rol) ? "Líder" : rol || "Integrante";
}

function AvatarFoto({
  idPersona,
  nombre,
  mio,
}: {
  idPersona: number;
  nombre: string;
  mio?: boolean;
}) {
  const [url, setUrl] = useState("");

  useEffect(() => {
    let vivo = true;
    let objectUrl = "";
    blobFotoPersona(idPersona)
      .then((blob) => {
        objectUrl = URL.createObjectURL(blob);
        if (vivo) setUrl(objectUrl);
      })
      .catch(() => undefined);
    return () => {
      vivo = false;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [idPersona]);

  if (url) {
    return (
      <img
        className={mio ? "mi-eq-msg-avatar mio" : "mi-eq-msg-avatar"}
        src={url}
        alt={nombre}
      />
    );
  }
  return (
    <div
      className={mio ? "mi-eq-msg-avatar mio" : "mi-eq-msg-avatar"}
      title={nombre}
    >
      {inicialNombre(nombre)}
    </div>
  );
}

function Media({ mensaje }: { mensaje: MensajeChat }) {
  const [url, setUrl] = useState("");

  useEffect(() => {
    if (!mensaje.tipo || mensaje.tipo === "TEXTO") return;
    let vivo = true;
    let objectUrl = "";
    blobArchivoChat(mensaje.id_mensaje)
      .then((blob) => {
        objectUrl = URL.createObjectURL(blob);
        if (vivo) setUrl(objectUrl);
      })
      .catch(() => undefined);
    return () => {
      vivo = false;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [mensaje.id_mensaje, mensaje.tipo]);

  if (mensaje.tipo === "IMAGEN") {
    return url ? <img src={url} alt={mensaje.nombre_archivo || ""} /> : null;
  }
  if (mensaje.tipo === "AUDIO") {
    return url ? <audio controls src={url} /> : null;
  }
  if (mensaje.tipo === "ARCHIVO") {
    return url ? (
      <a href={url} download={mensaje.nombre_archivo || "archivo"}>
        {mensaje.nombre_archivo || mensaje.contenido}
      </a>
    ) : (
      <span>{mensaje.nombre_archivo}</span>
    );
  }
  return <p>{mensaje.contenido}</p>;
}

function MiEquipo() {
  const { usuario } = useAuth();
  const miIdPersona = usuario?.id_persona ?? null;

  const [equipos, setEquipos] = useState<EquipoDetalle[]>([]);
  const [seleccionado, setSeleccionado] = useState<EquipoDetalle | null>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  const [mensajes, setMensajes] = useState<MensajeChat[]>([]);
  const [texto, setTexto] = useState("");
  const [cargandoChat, setCargandoChat] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [grabando, setGrabando] = useState(false);
  const [errorChat, setErrorChat] = useState("");

  const chatEndRef = useRef<HTMLDivElement | null>(null);
  const fileRef = useRef<HTMLInputElement | null>(null);
  const recRef = useRef<MediaRecorder | null>(null);

  useEffect(() => {
    const cargar = async () => {
      setCargando(true);
      setError("");
      try {
        const [misRels, todosEquipos, proyectos, personas] = await Promise.all([
          obtenerMisEquiposPersona(),
          obtenerEquipos(),
          obtenerProyectos(),
          obtenerPersonas(),
        ]);

        const mapaEquipos = new Map<number, Equipo>();
        todosEquipos.forEach((e) => mapaEquipos.set(e.id_equipo, e));
        const mapaProyectos = new Map<number, Proyecto>();
        proyectos.forEach((p) => mapaProyectos.set(p.id_proyecto, p));
        const mapaPersonas = new Map<number, Persona>();
        personas.forEach((p) => mapaPersonas.set(p.id_persona, p));

        const detalle: EquipoDetalle[] = [];
        for (const r of misRels.filter((item) => !item.fecha_fin)) {
          const eq = mapaEquipos.get(r.id_equipo);
          if (!eq) continue;
          const proy = mapaProyectos.get(eq.id_proyecto);
          let integrantesRel: EquipoPersonaItem[] = [];
          try {
            integrantesRel = await obtenerPersonasPorEquipo(r.id_equipo);
          } catch {
            integrantesRel = [];
          }
          detalle.push({
            id_equipo: eq.id_equipo,
            nombre: eq.nombre,
            id_proyecto: eq.id_proyecto,
            nombre_proyecto: proy?.nombre ?? `Proyecto #${eq.id_proyecto}`,
            miRol: r.rol_equipo,
            miDedicacion: Number(r.dedicacion),
            integrantes: integrantesRel
              .filter((i) => !i.fecha_fin)
              .map((i) => {
                const per = mapaPersonas.get(i.id_persona);
                return {
                  id_persona: i.id_persona,
                  nombre: per
                    ? `${per.nombre} ${per.apellido}`
                    : `Persona #${i.id_persona}`,
                  rol_equipo: i.rol_equipo,
                  dedicacion: Number(i.dedicacion),
                };
              }),
          });
        }

        setEquipos(detalle);
        if (detalle.length > 0) setSeleccionado(detalle[0]);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Error al cargar equipos",
        );
      } finally {
        setCargando(false);
      }
    };
    cargar();
  }, []);

  const cargarMensajes = useCallback(async (idEquipo: number) => {
    setCargandoChat(true);
    setErrorChat("");
    try {
      setMensajes(await obtenerMensajesBandeja(idEquipo));
    } catch (err) {
      setMensajes([]);
      setErrorChat(
        err instanceof Error ? err.message : "No se pudieron cargar mensajes",
      );
    } finally {
      setCargandoChat(false);
    }
  }, []);

  useEffect(() => {
    if (!seleccionado) {
      setMensajes([]);
      return;
    }
    cargarMensajes(seleccionado.id_equipo);
    const id = window.setInterval(
      () => cargarMensajes(seleccionado.id_equipo),
      5000,
    );
    return () => window.clearInterval(id);
  }, [seleccionado, cargarMensajes]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [mensajes]);

  const manejarEnvio = async (e: FormEvent) => {
    e.preventDefault();
    if (!seleccionado || !texto.trim() || enviando) return;
    setEnviando(true);
    setErrorChat("");
    try {
      await enviarMensajeEquipo(seleccionado.id_equipo, texto.trim());
      setTexto("");
      await cargarMensajes(seleccionado.id_equipo);
    } catch (err) {
      setErrorChat(
        err instanceof Error ? err.message : "No se pudo enviar el mensaje",
      );
    } finally {
      setEnviando(false);
    }
  };

  const subir = async (file: File | null) => {
    if (!file || !seleccionado) return;
    setEnviando(true);
    setErrorChat("");
    try {
      await enviarArchivoChat(seleccionado.id_equipo, file);
      await cargarMensajes(seleccionado.id_equipo);
    } catch (err) {
      setErrorChat(
        err instanceof Error ? err.message : "No se pudo subir el archivo",
      );
    } finally {
      setEnviando(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  const grabar = async () => {
    if (!seleccionado) return;
    if (grabando && recRef.current) {
      recRef.current.stop();
      setGrabando(false);
      return;
    }
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const rec = new MediaRecorder(stream);
    const partes: Blob[] = [];
    rec.ondataavailable = (e) => {
      if (e.data.size) partes.push(e.data);
    };
    rec.onstop = () => {
      stream.getTracks().forEach((t) => t.stop());
      const blob = new Blob(partes, { type: "audio/webm" });
      void subir(new File([blob], "audio.webm", { type: "audio/webm" }));
    };
    recRef.current = rec;
    rec.start();
    setGrabando(true);
  };

  if (cargando) return <div className="mi-eq-msg">Cargando tus equipos...</div>;
  if (error) return <div className="mi-eq-error">{error}</div>;

  return (
    <div className="mi-eq-page">
      <div className="mi-eq-layout">
        <section className="mi-eq-card">
          <h2>Mis equipos</h2>
          <p className="mi-eq-hint">
            Selecciona un equipo para ver integrantes y el chat.
          </p>
          {equipos.length === 0 ? (
            <p className="mi-eq-hint">No perteneces a ningún equipo activo.</p>
          ) : (
            <ul className="mi-eq-ul">
              {equipos.map((e) => (
                <li key={e.id_equipo}>
                  <button
                    type="button"
                    className={
                      seleccionado?.id_equipo === e.id_equipo
                        ? "mi-eq-item active"
                        : "mi-eq-item"
                    }
                    onClick={() => setSeleccionado(e)}
                  >
                    <strong>
                      {e.nombre}
                      {esLider(e.miRol) && (
                        <span className="mi-eq-lider">Líder</span>
                      )}
                    </strong>
                    <span>
                      {e.nombre_proyecto} · {textoRol(e.miRol)}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="mi-eq-card">
          {!seleccionado ? (
            <p className="mi-eq-hint">Elige un equipo.</p>
          ) : (
            <>
              <span className="mi-eq-label">EQUIPO</span>
              <h2>
                {seleccionado.nombre}
                {esLider(seleccionado.miRol) && (
                  <span className="mi-eq-lider">Líder</span>
                )}
              </h2>
              <p className="mi-eq-hint">
                Proyecto: {seleccionado.nombre_proyecto}
                <br />
                Tu rol: {textoRol(seleccionado.miRol)} · Dedicación:{" "}
                {seleccionado.miDedicacion}%
              </p>

              <h3 className="mi-eq-sub">Integrantes</h3>
              <ul className="mi-eq-members">
                {seleccionado.integrantes.map((m) => {
                  const soyYo =
                    miIdPersona != null &&
                    Number(m.id_persona) === Number(miIdPersona);
                  return (
                    <li key={m.id_persona}>
                      <strong>
                        {m.nombre}
                        {soyYo ? " · Tú" : ""}
                        {esLider(m.rol_equipo) && (
                          <span className="mi-eq-lider">Líder</span>
                        )}
                      </strong>
                      <span>
                        {textoRol(m.rol_equipo)} · {m.dedicacion}%
                      </span>
                    </li>
                  );
                })}
              </ul>

              <div className="mi-eq-chat">
                <div className="mi-eq-chat-header">
                  <strong>Chat del equipo</strong>
                  <span>Actualiza cada 5 s</span>
                </div>
                <div className="mi-eq-chat-messages">
                  {cargandoChat && mensajes.length === 0 ? (
                    <p className="mi-eq-hint">Cargando mensajes...</p>
                  ) : mensajes.length === 0 ? (
                    <p className="mi-eq-hint">
                      Aún no hay mensajes. Escribe el primero.
                    </p>
                  ) : (
                    mensajes.map((m) => {
                      const esMio =
                        miIdPersona != null &&
                        Number(m.id_persona) === Number(miIdPersona);
                      const esTexto = !m.tipo || m.tipo === "TEXTO";
                      return (
                        <div
                          key={m.id_mensaje}
                          className={
                            esMio ? "mi-eq-msg-row mio" : "mi-eq-msg-row otro"
                          }
                        >
                          {!esMio && (
                            <AvatarFoto
                              idPersona={m.id_persona}
                              nombre={m.nombre}
                            />
                          )}
                          <div
                            className={
                              esMio
                                ? "mi-eq-msg-bubble mio"
                                : "mi-eq-msg-bubble otro"
                            }
                          >
                            {!esMio && (
                              <div className="mi-eq-msg-name">{m.nombre}</div>
                            )}
                            {esTexto ? (
                              <p>{m.contenido}</p>
                            ) : (
                              <Media mensaje={m} />
                            )}
                            <span className="mi-eq-msg-time">
                              {new Date(m.fecha_envio).toLocaleTimeString([], {
                                hour: "2-digit",
                                minute: "2-digit",
                              })}
                            </span>
                          </div>
                          {esMio && (
                            <AvatarFoto
                              idPersona={m.id_persona}
                              nombre={usuario?.nombre_usuario || "Tú"}
                              mio
                            />
                          )}
                        </div>
                      );
                    })
                  )}
                  <div ref={chatEndRef} />
                </div>
                {errorChat && <p className="mi-eq-chat-error">{errorChat}</p>}
                <form className="mi-eq-chat-form" onSubmit={manejarEnvio}>
                  <input
                    ref={fileRef}
                    type="file"
                    hidden
                    accept="image/*,audio/*,.pdf,.doc,.docx,.xls,.xlsx,.zip,.txt"
                    onChange={(e) => subir(e.target.files?.[0] ?? null)}
                  />
                  <button
                    type="button"
                    onClick={() => fileRef.current?.click()}
                    disabled={enviando || grabando}
                  >
                    +
                  </button>
                  <button
                    type="button"
                    onClick={() => void grabar()}
                    disabled={enviando}
                  >
                    {grabando ? "Detener" : "Audio"}
                  </button>
                  <input
                    type="text"
                    value={texto}
                    onChange={(e) => setTexto(e.target.value)}
                    placeholder="Escribe un mensaje..."
                    maxLength={2000}
                    disabled={enviando}
                  />
                  <button type="submit" disabled={enviando || !texto.trim()}>
                    {enviando ? "..." : "Enviar"}
                  </button>
                </form>
              </div>
            </>
          )}
        </section>
      </div>
    </div>
  );
}

export default MiEquipo;
