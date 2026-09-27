export interface Proyecto {
  id_proyecto: number;
  nombre: string;
  descripcion: string | null;
  fecha_inicio: string;
  fecha_limite: string;
  estado: string;
  fecha_creacion: string;
}