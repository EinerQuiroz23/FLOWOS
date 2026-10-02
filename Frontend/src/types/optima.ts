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

export interface LiderPropuesto {
  id_persona: number;
  persona: string;
  compatibilidad: number;
  experiencia: number;
  disponibilidad: number;
  puntuacion_liderazgo: number;
  confianza?: string | null;
  habilidades_ok?: string | null;
  habilidades_no_registradas?: string | null;
  habilidades_nivel_insuficiente?: string | null;
  explicacion?: string | null;
}

export interface IntegrantePropuesto {
  id_persona: number;
  persona: string;
  capacidad_horas_semana: number;
  horas_carga_actual: number;
  disponibilidad: number;
  habilidades_requeridas: number;
  habilidades_cumplidas: number;
  compatibilidad: number;
  años_experiencia_promedio: number;
  experiencia: number;
  puntuacion_equipo: number;
  habilidades_ok?: string | null;
  habilidades_no_registradas?: string | null;
  habilidades_nivel_insuficiente?: string | null;
  contribucion?: string | null;
}

export interface PropuestaEquipo {
  id_proyecto: number;
  proyecto: string;
  cobertura: number;
  integrantes_recomendados: number;
  integrantes_analizados: number;
  lider: LiderPropuesto | null;
  lider_alternativo?: LiderPropuesto | null;
  integrantes: IntegrantePropuesto[];
  habilidades_requeridas: number;
  habilidades_cubiertas: number;
  habilidades_faltantes?: string | null;
  explicacion: string;
  puede_crearse: boolean;
  confianza_liderazgo?: string | null;
  riesgos_detectados?: string[];
  recomendaciones?: string[];
}
