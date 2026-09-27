export interface Usuario {
  id_usuario: number;
  id_organizacion: number;
  id_persona: number;
  id_rol: number;
  nombre_usuario: string;
  email: string;
  estado: boolean;
  fecha_creacion: string;
  ultimo_acceso: string | null;
}

export interface UsuarioCreate {
  id_persona: number;
  id_rol: number;
  nombre_usuario: string;
  email: string;
  contrasena: string;
}

export interface UsuarioUpdate {
  id_rol?: number;
  nombre_usuario?: string;
  email?: string;
  estado?: boolean;
}
