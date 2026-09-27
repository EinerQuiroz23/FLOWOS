export interface Equipo {
  id_equipo: number;
  id_proyecto: number;
  nombre: string;
  descripcion: string | null;
  estado: string;
  fecha_creacion: string;
}
