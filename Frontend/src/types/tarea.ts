export interface Tarea {
  id_tarea: number;
  id_proyecto: number;
  id_equipo: number;
  nombre: string;
  descripcion: string | null;
  prioridad: string;
  horas_estimadas: number;
  fecha_inicio: string;
  fecha_limite: string;
  estado: string;
  fecha_creacion: string;
}
