export interface Persona {
  id_persona: number;
  nombre: string;
  apellido: string;
  email: string;
  telefono: string | null;
  capacidad_horas_semana: number;
  estado: boolean;
  fecha_creacion: string;
}
