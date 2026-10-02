import type { Proyecto } from "../types/proyecto";
import type { Persona } from "../types/persona";
import type { Equipo } from "../types/equipo";
import type { Tarea } from "../types/tarea";
import type { CandidatoOptima } from "../types/optima";
import type { Usuario, UsuarioCreate, UsuarioUpdate } from "../types/usuario";
import type { Rol } from "../types/rol";
import type { PropuestaEquipo } from "../types/optima";

const API_URL = "http://127.0.0.1:8000";

function obtenerHeaders(): HeadersInit {
  const token = localStorage.getItem("flowos_token");

  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

async function procesarRespuesta<T>(respuesta: Response): Promise<T> {
  if (respuesta.status === 401) {
    localStorage.removeItem("flowos_token");
    window.location.href = "/login";

    throw new Error("La sesión ha expirado.");
  }

  if (!respuesta.ok) {
    let mensaje = "Ocurrió un error al comunicarse con FLOWOS.";

    try {
      const error = await respuesta.json();

      if (error.detail) {
        mensaje = error.detail;
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

// =========================================================
// PERSONAS
// =========================================================

export async function obtenerPersonas(): Promise<Persona[]> {
  const respuesta = await fetch(`${API_URL}/personas`, {
    headers: obtenerHeaders(),
  });

  return procesarRespuesta<Persona[]>(respuesta);
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

// =========================================================
// TAREAS
// =========================================================

export async function obtenerTareas(): Promise<Tarea[]> {
  const respuesta = await fetch(`${API_URL}/tareas`, {
    headers: obtenerHeaders(),
  });

  return procesarRespuesta<Tarea[]>(respuesta);
}

// =========================================================
// OPTIMA
// =========================================================

export async function evaluarTareaOptima(
  idTarea: number,
): Promise<CandidatoOptima[]> {
  const respuesta = await fetch(`${API_URL}/optima/tarea/${idTarea}`, {
    headers: obtenerHeaders(),
  });

  return procesarRespuesta<CandidatoOptima[]>(respuesta);
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

export async function obtenerMiPersona(): Promise<Persona> {
  const respuesta = await fetch(`${API_URL}/personas/me`, {
    headers: obtenerHeaders(),
  });
  return procesarRespuesta<Persona>(respuesta);
}

export async function obtenerMisTareas(): Promise<MiTarea[]> {
  const respuesta = await fetch(`${API_URL}/tareas/mias`, {
    headers: obtenerHeaders(),
  });
  return procesarRespuesta<MiTarea[]>(respuesta);
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

// Si aún no tienes detalle por id:
export async function obtenerEquipo(idEquipo: number): Promise<Equipo> {
  const respuesta = await fetch(`${API_URL}/equipos/${idEquipo}`, {
    headers: obtenerHeaders(),
  });
  return procesarRespuesta<Equipo>(respuesta);
}

export async function obtenerProyecto(idProyecto: number): Promise<Proyecto> {
  const respuesta = await fetch(`${API_URL}/proyectos/${idProyecto}`, {
    headers: obtenerHeaders(),
  });
  return procesarRespuesta<Proyecto>(respuesta);
}

export async function obtenerTareasPorProyecto(
  idProyecto: number,
): Promise<Tarea[]> {
  const respuesta = await fetch(`${API_URL}/tareas/proyecto/${idProyecto}`, {
    headers: obtenerHeaders(),
  });
  return procesarRespuesta<Tarea[]>(respuesta);
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
