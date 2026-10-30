import type { Proyecto } from "../types/proyecto";
import type { Persona } from "../types/persona";
import type { Equipo } from "../types/equipo";
import type { Tarea } from "../types/tarea";
import type { CandidatoOptima, PropuestaEquipo } from "../types/optima";
import type { Usuario, UsuarioCreate, UsuarioUpdate } from "../types/usuario";
import type { Rol } from "../types/rol";

const API_URL = "http://127.0.0.1:8000";

function obtenerHeaders(): HeadersInit {
  const token = sessionStorage.getItem("flowos_token");

  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

async function procesarRespuesta<T>(respuesta: Response): Promise<T> {
  if (respuesta.status === 401) {
    sessionStorage.removeItem("flowos_token");
    window.location.href = "/login";

    throw new Error("La sesión ha expirado.");
  }

  if (!respuesta.ok) {
    let mensaje = "Ocurrió un error al comunicarse con FLOWOS.";

    try {
      const error = await respuesta.json();

      if (error.detail) {
        mensaje =
          typeof error.detail === "string"
            ? error.detail
            : JSON.stringify(error.detail);
      }

      if (error.message) {
        mensaje = error.message;
      }
    } catch {
      // Se conserva el mensaje por defecto.
    }

    throw new Error(mensaje);
  }

  return respuesta.json();
}

// =========================================================
// PROYECTOS
// =========================================================

export async function obtenerProyectos(): Promise<Proyecto[]> {
  const respuesta = await fetch(`${API_URL}/proyectos`, {
    headers: obtenerHeaders(),
  });

  return procesarRespuesta<Proyecto[]>(respuesta);
}

export async function obtenerProyecto(idProyecto: number): Promise<Proyecto> {
  const respuesta = await fetch(`${API_URL}/proyectos/${idProyecto}`, {
    headers: obtenerHeaders(),
  });
  return procesarRespuesta<Proyecto>(respuesta);
}

// =========================================================
// PERSONAS
// =========================================================

export async function obtenerPersonas(): Promise<Persona[]> {
  const respuesta = await fetch(`${API_URL}/personas`, {
    headers: obtenerHeaders(),
  });

  return procesarRespuesta<Persona[]>(respuesta);
}

export async function obtenerMiPersona(): Promise<Persona> {
  const respuesta = await fetch(`${API_URL}/personas/me`, {
    headers: obtenerHeaders(),
  });
  return procesarRespuesta<Persona>(respuesta);
}

// =========================================================
// EQUIPOS
// =========================================================

export async function obtenerEquipos(): Promise<Equipo[]> {
  const respuesta = await fetch(`${API_URL}/equipos`, {
    headers: obtenerHeaders(),
  });

  return procesarRespuesta<Equipo[]>(respuesta);
}

export async function obtenerEquipo(idEquipo: number): Promise<Equipo> {
  const respuesta = await fetch(`${API_URL}/equipos/${idEquipo}`, {
    headers: obtenerHeaders(),
  });
  return procesarRespuesta<Equipo>(respuesta);
}

// =========================================================
// TAREAS
// =========================================================

export async function obtenerTareas(): Promise<Tarea[]> {
  const respuesta = await fetch(`${API_URL}/tareas`, {
    headers: obtenerHeaders(),
  });

  return procesarRespuesta<Tarea[]>(respuesta);
}

export async function obtenerTareasPorProyecto(
  idProyecto: number,
): Promise<Tarea[]> {
  const respuesta = await fetch(`${API_URL}/tareas/proyecto/${idProyecto}`, {
    headers: obtenerHeaders(),
  });
  return procesarRespuesta<Tarea[]>(respuesta);
}

export interface MiTarea {
  id_asignacion: number;
  id_tarea: number;
  nombre_tarea: string;
  id_proyecto: number;
  id_equipo: number;
  prioridad: string | null;
  estado_tarea: string | null;
  estado_asignacion: string;
  dedicacion: number;
  fecha_inicio: string;
  fecha_limite: string;
  horas_estimadas: number | null;
}

export async function obtenerMisTareas(): Promise<MiTarea[]> {
  const respuesta = await fetch(`${API_URL}/tareas/mias`, {
    headers: obtenerHeaders(),
  });
  return procesarRespuesta<MiTarea[]>(respuesta);
}

// =========================================================
// OPTIMA
// =========================================================

export type AlcanceOptima = "equipo" | "proyecto" | "organizacion";

export async function evaluarTareaOptima(
  idTarea: number,
  alcance: string = "equipo",
): Promise<CandidatoOptima[]> {
  const respuesta = await fetch(
    `${API_URL}/optima/tarea/${idTarea}?alcance=${alcance}`,
    { headers: obtenerHeaders() },
  );
  return procesarRespuesta<CandidatoOptima[]>(respuesta);
}

export async function proponerEquipoOptima(
  idProyecto: number,
): Promise<PropuestaEquipo> {
  const respuesta = await fetch(
    `${API_URL}/optima/proyecto/${idProyecto}/propuesta-equipo`,
    {
      headers: obtenerHeaders(),
    },
  );

  return procesarRespuesta<PropuestaEquipo>(respuesta);
}

export interface OptimaConfirmarResponse {
  id_proyecto: number;
  id_equipo: number;
  nombre_equipo: string;
  id_lider: number | null;
  integrantes_agregados: number;
  asignaciones_creadas: number;
  detalle_asignaciones: {
    id_asignacion: number;
    id_tarea: number;
    nombre_tarea: string;
    id_persona: number;
    persona: string;
  }[];
  mensaje: string;
}

export async function confirmarPropuestaOptima(
  idProyecto: number,
  nombreEquipo?: string,
): Promise<OptimaConfirmarResponse> {
  const respuesta = await fetch(
    `${API_URL}/optima/proyecto/${idProyecto}/confirmar`,
    {
      method: "POST",
      headers: obtenerHeaders(),
      body: JSON.stringify({
        nombre_equipo: nombreEquipo || null,
      }),
    },
  );
  return procesarRespuesta<OptimaConfirmarResponse>(respuesta);
}

// =========================================================
// USUARIOS
// =========================================================

export async function obtenerUsuarios(): Promise<Usuario[]> {
  const respuesta = await fetch(`${API_URL}/usuarios/`, {
    headers: obtenerHeaders(),
  });

  return procesarRespuesta<Usuario[]>(respuesta);
}

export async function obtenerUsuario(idUsuario: number): Promise<Usuario> {
  const respuesta = await fetch(`${API_URL}/usuarios/${idUsuario}`, {
    headers: obtenerHeaders(),
  });

  return procesarRespuesta<Usuario>(respuesta);
}

export async function crearUsuario(datos: UsuarioCreate): Promise<Usuario> {
  const respuesta = await fetch(`${API_URL}/usuarios/`, {
    method: "POST",
    headers: obtenerHeaders(),
    body: JSON.stringify(datos),
  });

  return procesarRespuesta<Usuario>(respuesta);
}

export async function actualizarUsuario(
  idUsuario: number,
  datos: UsuarioUpdate,
): Promise<Usuario> {
  const respuesta = await fetch(`${API_URL}/usuarios/${idUsuario}`, {
    method: "PUT",
    headers: obtenerHeaders(),
    body: JSON.stringify(datos),
  });

  return procesarRespuesta<Usuario>(respuesta);
}

export async function activarUsuario(idUsuario: number): Promise<Usuario> {
  const respuesta = await fetch(`${API_URL}/usuarios/${idUsuario}/activar`, {
    method: "PATCH",
    headers: obtenerHeaders(),
  });

  return procesarRespuesta<Usuario>(respuesta);
}

export async function desactivarUsuario(idUsuario: number): Promise<Usuario> {
  const respuesta = await fetch(`${API_URL}/usuarios/${idUsuario}/desactivar`, {
    method: "PATCH",
    headers: obtenerHeaders(),
  });

  return procesarRespuesta<Usuario>(respuesta);
}

export async function obtenerRoles(): Promise<Rol[]> {
  const respuesta = await fetch(`${API_URL}/roles`, {
    headers: obtenerHeaders(),
  });

  return procesarRespuesta<Rol[]>(respuesta);
}

export async function cambiarNombreUsuario(nombre_usuario: string): Promise<{
  mensaje: string;
  nombre_usuario: string;
}> {
  const respuesta = await fetch(`${API_URL}/usuarios/me/nombre-usuario`, {
    method: "PATCH",
    headers: obtenerHeaders(),
    body: JSON.stringify({ nombre_usuario }),
  });

  return procesarRespuesta<{
    mensaje: string;
    nombre_usuario: string;
  }>(respuesta);
}

// =========================================================
// HABILIDADES DEL EMPLEADO
// =========================================================

export interface Habilidad {
  id_habilidad: number;
  nombre: string;
  descripcion?: string | null;
  estado?: boolean;
}

export interface NivelHabilidad {
  id_nivel: number;
  nombre: string;
  descripcion?: string | null;
}

export interface PersonaHabilidad {
  id_persona_habilidad: number;
  id_persona: number;
  id_habilidad: number;
  id_nivel: number;
  años_experiencia: number;
}

export async function obtenerHabilidades(): Promise<Habilidad[]> {
  const respuesta = await fetch(`${API_URL}/habilidades/`, {
    headers: obtenerHeaders(),
  });
  return procesarRespuesta<Habilidad[]>(respuesta);
}

export async function obtenerNivelesHabilidad(): Promise<NivelHabilidad[]> {
  const respuesta = await fetch(`${API_URL}/niveles-habilidad/`, {
    headers: obtenerHeaders(),
  });
  return procesarRespuesta<NivelHabilidad[]>(respuesta);
}

export async function obtenerMisHabilidades(): Promise<PersonaHabilidad[]> {
  const respuesta = await fetch(`${API_URL}/personas-habilidades/me`, {
    headers: obtenerHeaders(),
  });
  return procesarRespuesta<PersonaHabilidad[]>(respuesta);
}

export async function crearMiHabilidad(datos: {
  id_persona: number;
  id_habilidad: number;
  id_nivel: number;
  años_experiencia: number;
}): Promise<PersonaHabilidad> {
  const respuesta = await fetch(`${API_URL}/personas-habilidades/me`, {
    method: "POST",
    headers: obtenerHeaders(),
    body: JSON.stringify(datos),
  });
  return procesarRespuesta<PersonaHabilidad>(respuesta);
}

// =========================================================
// EQUIPOS - PERSONAS
// =========================================================

export interface EquipoPersonaItem {
  id_equipo_persona: number;
  id_equipo: number;
  id_persona: number;
  rol_equipo: string;
  dedicacion: number;
  fecha_inicio: string;
  fecha_fin: string | null;
}

export async function obtenerMisEquiposPersona(): Promise<EquipoPersonaItem[]> {
  const respuesta = await fetch(`${API_URL}/equipos-personas/me`, {
    headers: obtenerHeaders(),
  });
  return procesarRespuesta<EquipoPersonaItem[]>(respuesta);
}

export async function obtenerPersonasPorEquipo(
  idEquipo: number,
): Promise<EquipoPersonaItem[]> {
  const respuesta = await fetch(
    `${API_URL}/equipos-personas/equipo/${idEquipo}`,
    { headers: obtenerHeaders() },
  );
  return procesarRespuesta<EquipoPersonaItem[]>(respuesta);
}

export interface OcupacionPersona {
  id_persona: number;
  capacidad_horas_semana: number;
  ocupacion_pct: number;
  disponibilidad_pct: number;
}

export async function obtenerOcupacionPersona(
  idPersona: number,
): Promise<OcupacionPersona> {
  const respuesta = await fetch(`${API_URL}/personas/${idPersona}/ocupacion`, {
    headers: obtenerHeaders(),
  });
  return procesarRespuesta<OcupacionPersona>(respuesta);
}

export interface MensajeEquipo {
  id_mensaje: number;
  id_equipo: number;
  id_persona: number;
  nombre_persona: string;
  contenido: string;
  fecha_creacion: string;
}

export async function obtenerMensajesEquipo(
  idEquipo: number,
): Promise<MensajeEquipo[]> {
  const respuesta = await fetch(`${API_URL}/chat/equipo/${idEquipo}/mensajes`, {
    headers: obtenerHeaders(),
  });
  return procesarRespuesta<MensajeEquipo[]>(respuesta);
}

export async function enviarMensajeEquipo(
  idEquipo: number,
  contenido: string,
): Promise<MensajeEquipo> {
  const respuesta = await fetch(`${API_URL}/chat/equipo/${idEquipo}/mensajes`, {
    method: "POST",
    headers: obtenerHeaders(),
    body: JSON.stringify({ contenido }),
  });
  return procesarRespuesta<MensajeEquipo>(respuesta);
}

export interface OrganizacionItem {
  id_organizacion: number;
  nombre: string;
  descripcion?: string | null;
  estado: boolean;
  fecha_creacion?: string;
  codigo_organizacion?: string | null;
}

export async function listarOrganizaciones(): Promise<OrganizacionItem[]> {
  const respuesta = await fetch(`${API_URL}/organizaciones`, {
    headers: obtenerHeaders(),
  });
  return procesarRespuesta<OrganizacionItem[]>(respuesta);
}

export interface PersonaCreate {
  nombre: string;
  apellido: string;
  email: string;
  telefono?: string | null;
  capacidad_horas_semana: number;
}

export async function crearPersona(datos: PersonaCreate): Promise<Persona> {
  const respuesta = await fetch(`${API_URL}/personas/`, {
    method: "POST",
    headers: obtenerHeaders(),
    body: JSON.stringify(datos),
  });
  return procesarRespuesta<Persona>(respuesta);
}

export interface ProyectoCreate {
  nombre: string;
  descripcion?: string | null;
  fecha_inicio: string;
  fecha_limite: string;
}

export async function crearProyecto(datos: ProyectoCreate): Promise<Proyecto> {
  const respuesta = await fetch(`${API_URL}/proyectos/`, {
    method: "POST",
    headers: obtenerHeaders(),
    body: JSON.stringify(datos),
  });
  return procesarRespuesta<Proyecto>(respuesta);
}

export async function listarPersonasOrganizacion(
  idOrganizacion: number,
): Promise<
  {
    id_persona: number;
    nombre: string;
    apellido: string;
    email: string;
    estado: boolean;
  }[]
> {
  const respuesta = await fetch(
    `${API_URL}/organizaciones/${idOrganizacion}/personas`,
    { headers: obtenerHeaders() },
  );
  return procesarRespuesta(respuesta);
}

export async function promoverAdminOrganizacion(
  idOrganizacion: number,
  idPersona: number,
  contrasena?: string,
) {
  const respuesta = await fetch(
    `${API_URL}/organizaciones/${idOrganizacion}/admin/promover`,
    {
      method: "POST",
      headers: obtenerHeaders(),
      body: JSON.stringify({
        id_persona: idPersona,
        contrasena: contrasena || null,
      }),
    },
  );
  return procesarRespuesta(respuesta);
}

export interface TareaCreate {
  id_proyecto: number;
  id_equipo: number;
  nombre: string;
  descripcion?: string | null;
  prioridad?: string;
  horas_estimadas: number;
  fecha_inicio: string;
  fecha_limite: string;
}

export async function crearTarea(datos: TareaCreate): Promise<Tarea> {
  const respuesta = await fetch(`${API_URL}/tareas/`, {
    method: "POST",
    headers: obtenerHeaders(),
    body: JSON.stringify(datos),
  });
  return procesarRespuesta<Tarea>(respuesta);
}

export interface MensajeChat {
  id_mensaje: number;
  id_equipo: number;
  id_persona: number;
  nombre: string;
  contenido: string;
  tipo: "TEXTO" | "IMAGEN" | "AUDIO" | "ARCHIVO" | string;
  nombre_archivo?: string | null;
  tiene_foto?: boolean;
  fecha_envio: string;
}

export async function obtenerMensajesBandeja(
  idEquipo: number,
): Promise<MensajeChat[]> {
  const respuesta = await fetch(`${API_URL}/chat/equipo/${idEquipo}/bandeja`, {
    headers: obtenerHeaders(),
  });
  return procesarRespuesta<MensajeChat[]>(respuesta);
}

export async function enviarMensajeBandeja(
  idEquipo: number,
  contenido: string,
) {
  const respuesta = await fetch(`${API_URL}/chat/equipo/${idEquipo}/bandeja`, {
    method: "POST",
    headers: obtenerHeaders(),
    body: JSON.stringify({ contenido }),
  });
  return procesarRespuesta<MensajeChat>(respuesta);
}

export async function enviarArchivoChat(idEquipo: number, archivo: File) {
  const token = sessionStorage.getItem("flowos_token");
  const body = new FormData();
  body.append("archivo", archivo);
  const respuesta = await fetch(`${API_URL}/chat/equipo/${idEquipo}/archivo`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body,
  });
  return procesarRespuesta<MensajeChat>(respuesta);
}

export async function blobArchivoChat(idMensaje: number): Promise<Blob> {
  const token = sessionStorage.getItem("flowos_token");
  const respuesta = await fetch(`${API_URL}/chat/archivo/${idMensaje}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!respuesta.ok) throw new Error("No se pudo abrir el archivo");
  return respuesta.blob();
}

export async function borrarChatParaMi(idEquipo: number) {
  const respuesta = await fetch(`${API_URL}/chat/equipo/${idEquipo}/para-mi`, {
    method: "DELETE",
    headers: obtenerHeaders(),
  });
  if (!respuesta.ok && respuesta.status !== 204) {
    throw new Error("No se pudo borrar la conversación");
  }
}

export async function obtenerMisEquiposChat(): Promise<Equipo[]> {
  const respuesta = await fetch(`${API_URL}/chat/mis-equipos`, {
    headers: obtenerHeaders(),
  });
  return procesarRespuesta<Equipo[]>(respuesta);
}

export async function subirMiFoto(archivo: File) {
  const token = sessionStorage.getItem("flowos_token");
  const data = new FormData();
  data.append("archivo", archivo);
  const respuesta = await fetch(`${API_URL}/personas/mi-foto`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: data,
  });
  return procesarRespuesta<{ ok: boolean }>(respuesta);
}

export async function blobFotoPersona(idPersona: number) {
  const token = sessionStorage.getItem("flowos_token");
  const respuesta = await fetch(`${API_URL}/personas/foto/${idPersona}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!respuesta.ok) throw new Error("Sin foto");
  return respuesta.blob();
}
