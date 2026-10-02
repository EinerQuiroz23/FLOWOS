export const ROLES = {
  ADMIN: 1,
  LIDER_PROYECTO: 2,
  SECRETARIO: 3,
  EMPLEADO: 4,
  SUPER_ADMIN: 5,
} as const;

export function obtenerRutaPorRol(idRol: number): string {
  switch (idRol) {
    case ROLES.SUPER_ADMIN:
      return "/organizaciones"; // panel de organizaciones
    case ROLES.ADMIN:
      return "/dashboard";
    case ROLES.SECRETARIO:
      return "/dashboard";
    case ROLES.EMPLEADO:
      return "/mi-panel"; // panel del empleado
    case ROLES.LIDER_PROYECTO:
      return "/dashboard";
    default:
      return "/dashboard";
  }
}

export function nombreRol(idRol: number): string {
  switch (idRol) {
    case 1:
      return "ADMIN";
    case 2:
      return "LIDER_PROYECTO";
    case 3:
      return "SECRETARIO";
    case 4:
      return "EMPLEADO";
    case 5:
      return "SUPER_ADMIN";
    default:
      return "DESCONOCIDO";
  }
}
