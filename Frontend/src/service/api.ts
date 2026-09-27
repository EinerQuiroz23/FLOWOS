import type { Proyecto } from "../types/proyecto";
import type { Persona } from "../types/persona";
import type { Equipo } from "../types/equipo";
import type { Tarea } from "../types/tarea";
import type { CandidatoOptima } from "../types/optima";
import type { Usuario, UsuarioCreate, UsuarioUpdate } from "../types/usuario";
import type { Rol } from "../types/rol";

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
