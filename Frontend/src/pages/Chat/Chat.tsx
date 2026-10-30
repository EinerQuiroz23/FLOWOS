import { useEffect, useRef, useState, type FormEvent } from "react";
import { useSearchParams } from "react-router-dom";

import {
  obtenerMisEquiposChat,
  obtenerMensajesBandeja,
  enviarMensajeBandeja,
  enviarArchivoChat,
  borrarChatParaMi,
  blobArchivoChat,
  blobFotoPersona,
} from "../../service/api";
import { useAuth } from "../../context/AuthContext";
import type { Equipo } from "../../types/equipo";

import "./Chat.css";

type Mensaje = {
  id_mensaje: number;
  id_persona: number;
  nombre?: string;
  contenido?: string;
  tipo?: string;
  nombre_archivo?: string | null;
  tiene_foto?: boolean;
  fecha_envio?: string;
};

function iniciales(nombre: string) {
  const partes = nombre.trim().split(/\s+/);
  return ((partes[0]?.[0] ?? "") + (partes[1]?.[0] ?? "")).toUpperCase() || "?";
}

function hora(fecha?: string) {
  if (!fecha) return "";
  const d = new Date(fecha);
  if (Number.isNaN(d.getTime())) return "";
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function AvatarPersona({
  idPersona,
  nombre,
}: {
  idPersona: number;
  nombre: string;
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

  if (url) return <img className="chat-avatar" src={url} alt={nombre} />;
  return <span className="chat-avatar">{iniciales(nombre)}</span>;
}

function formatoAudio(seg: number) {
  if (!Number.isFinite(seg) || seg < 0) return "0:00";
  const m = Math.floor(seg / 60);
  const s = Math.floor(seg % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

function Reproductor({ src }: { src: string }) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [playing, setPlaying] = useState(false);
  const [tiempo, setTiempo] = useState(0);
  const [duracion, setDuracion] = useState(0);

  const toggle = () => {
    const el = audioRef.current;
    if (!el) return;
    if (el.paused) {
      void el.play();
      setPlaying(true);
    } else {
      el.pause();
      setPlaying(false);
    }
  };

  return (
    <div className="chat-audio">
      <button type="button" onClick={toggle}>
        {playing ? "II" : "▶"}
      </button>
      <input
        type="range"
        min={0}
        max={duracion || 0}
        step={0.1}
        value={Math.min(tiempo, duracion || 0)}
        onChange={(e) => {
          const valor = Number(e.target.value);
          if (audioRef.current) audioRef.current.currentTime = valor;
          setTiempo(valor);
        }}
      />
      <span>
        {formatoAudio(duracion ? (playing ? tiempo : duracion) : tiempo)}
      </span>
      <audio
        ref={audioRef}
        src={src}
        preload="metadata"
        onLoadedMetadata={(e) => setDuracion(e.currentTarget.duration || 0)}
        onTimeUpdate={(e) => setTiempo(e.currentTarget.currentTime)}
        onEnded={() => {
          setPlaying(false);
          setTiempo(0);
        }}
      />
    </div>
  );
}

function Media({ mensaje }: { mensaje: Mensaje }) {
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
    return url ? <Reproductor src={url} /> : <span>Cargando audio...</span>;
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

function Chat() {
  const { usuario } = useAuth();
  const [params, setParams] = useSearchParams();
  const [equipos, setEquipos] = useState<Equipo[]>([]);
  const [idEquipo, setIdEquipo] = useState(Number(params.get("equipo") || 0));
  const [mensajes, setMensajes] = useState<Mensaje[]>([]);
  const [texto, setTexto] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [grabando, setGrabando] = useState(false);
  const [error, setError] = useState("");
  const caja = useRef<HTMLDivElement>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const recRef = useRef<MediaRecorder | null>(null);

  const abrir = (id: number) => {
    setIdEquipo(id);
    setParams({ equipo: String(id) });
  };

  useEffect(() => {
    obtenerMisEquiposChat()
      .then((lista) => {
        const datos = Array.isArray(lista) ? lista : [];
        setEquipos(datos);
        const desdeUrl = Number(params.get("equipo") || 0);
        const permitido = datos.some((e) => e.id_equipo === desdeUrl);
        if (permitido) setIdEquipo(desdeUrl);
        else if (datos[0]) abrir(datos[0].id_equipo);
        else setIdEquipo(0);
      })
      .catch((err) => {
        setError(
          err instanceof Error ? err.message : "No se cargaron los equipos",
        );
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!idEquipo) {
      setMensajes([]);
      return;
    }
    let vivo = true;
    const cargar = async () => {
      try {
        const datos = await obtenerMensajesBandeja(idEquipo);
        if (vivo) {
          setMensajes(Array.isArray(datos) ? datos : []);
          setError("");
        }
      } catch (err) {
        if (vivo)
          setError(err instanceof Error ? err.message : "No se cargó el chat");
      }
    };
    cargar();
    const timer = window.setInterval(cargar, 2000);
    return () => {
      vivo = false;
      window.clearInterval(timer);
    };
  }, [idEquipo]);

  useEffect(() => {
    const el = caja.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [mensajes]);

  const actual = equipos.find((e) => e.id_equipo === idEquipo);

  const enviar = async (e: FormEvent) => {
    e.preventDefault();
    const contenido = texto.trim();
    if (!idEquipo || !contenido || enviando) return;
    setEnviando(true);
    try {
      await enviarMensajeBandeja(idEquipo, contenido);
      setTexto("");
      const datos = await obtenerMensajesBandeja(idEquipo);
      setMensajes(Array.isArray(datos) ? datos : []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo enviar");
    } finally {
      setEnviando(false);
    }
  };

  const subir = async (file: File | null) => {
    if (!file || !idEquipo) return;
    setEnviando(true);
    try {
      await enviarArchivoChat(idEquipo, file);
      const datos = await obtenerMensajesBandeja(idEquipo);
      setMensajes(Array.isArray(datos) ? datos : []);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "No se pudo subir el archivo",
      );
    } finally {
      setEnviando(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  const grabar = async () => {
    if (!idEquipo) return;
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

  const borrar = async () => {
    if (!idEquipo) return;
    const ok = window.confirm(
      "Se ocultará esta conversación solo para ti. Los demás la siguen viendo.",
    );
    if (!ok) return;
    await borrarChatParaMi(idEquipo);
    setMensajes([]);
  };

  return (
    <section className="chat-page">
      <aside className="chat-teams">
        <div className="chat-teams-head">
          <span>Mensajes</span>
          <h1>Chat</h1>
        </div>
        {equipos.length === 0 ? (
          <p className="chat-side-empty">No perteneces a ningún equipo.</p>
        ) : (
          <ul>
            {equipos.map((eq) => (
              <li key={eq.id_equipo}>
                <button
                  type="button"
                  className={eq.id_equipo === idEquipo ? "active" : ""}
                  onClick={() => abrir(eq.id_equipo)}
                >
                  <span>{iniciales(eq.nombre)}</span>
                  <strong>{eq.nombre}</strong>
                </button>
              </li>
            ))}
          </ul>
        )}
      </aside>

      <div className="chat-main">
        {!idEquipo ? (
          <div className="chat-empty">
            <h2>Sin conversación</h2>
            <p>Cuando te asignen a un equipo, el chat aparece aquí.</p>
          </div>
        ) : (
          <>
            <header className="chat-head">
              <div className="chat-head-id">
                <span>{iniciales(actual?.nombre || "Equipo")}</span>
                <div>
                  <strong>{actual?.nombre ?? `Equipo #${idEquipo}`}</strong>
                  <small>Solo integrantes de este equipo</small>
                </div>
              </div>
              <button type="button" className="chat-clear" onClick={borrar}>
                Borrar para mí
              </button>
            </header>

            {error && <p className="chat-error">{error}</p>}

            <div className="chat-box" ref={caja}>
              {mensajes.length === 0 && (
                <p className="chat-box-empty">
                  Aún no hay mensajes. Escribe abajo.
                </p>
              )}
              {mensajes.map((m) => {
                const mio = m.id_persona === usuario?.id_persona;
                const esTexto = !m.tipo || m.tipo === "TEXTO";
                return (
                  <div
                    key={m.id_mensaje}
                    className={mio ? "chat-row mio" : "chat-row"}
                  >
                    <AvatarPersona
                      idPersona={m.id_persona}
                      nombre={m.nombre || "Usuario"}
                    />
                    <div className={mio ? "chat-bubble mio" : "chat-bubble"}>
                      {!mio && (
                        <span className="chat-name">
                          {m.nombre || "Usuario"}
                        </span>
                      )}
                      {esTexto ? <p>{m.contenido}</p> : <Media mensaje={m} />}
                      <time>{hora(m.fecha_envio)}</time>
                    </div>
                  </div>
                );
              })}
            </div>

            <form className="chat-form" onSubmit={enviar}>
              <input
                ref={fileRef}
                type="file"
                hidden
                accept="image/*,audio/*,.pdf,.doc,.docx,.xls,.xlsx,.zip,.txt"
                onChange={(e) => subir(e.target.files?.[0] ?? null)}
              />
              <button
                type="button"
                className="chat-clip"
                onClick={() => fileRef.current?.click()}
                disabled={enviando || grabando}
              >
                +
              </button>
              <button
                type="button"
                className="chat-clip"
                onClick={() => void grabar()}
                disabled={enviando}
              >
                {grabando ? "Detener" : "Audio"}
              </button>
              <input
                value={texto}
                placeholder="Escribe un mensaje"
                onChange={(e) => setTexto(e.target.value)}
              />
              <button type="submit" disabled={enviando || !texto.trim()}>
                Enviar
              </button>
            </form>
          </>
        )}
      </div>
    </section>
  );
}

export default Chat;
