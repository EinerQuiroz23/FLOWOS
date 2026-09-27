export interface CandidatoOptima {
  id_tarea: number;
  tarea: string;
  id_persona: number;
  persona: string;
  capacidad_horas_semana: number;

  habilidades_requeridas: number;
  habilidades_cumplidas: number;

  compatibilidad: number | null;

  años_experiencia_promedio: number | null;
  experiencia: number | null;

  horas_carga_actual: number | null;
  disponibilidad: number | null;

  elegible: boolean | null;
  puntuacion_optima: number | null;

  habilidades_ok: string | null;
  habilidades_no_registradas: string | null;
  habilidades_nivel_insuficiente: string | null;

  ranking: number | null;
  explicacion: string | null;
}
