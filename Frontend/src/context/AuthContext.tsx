import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

interface UsuarioActual {
  id_usuario: number;
  id_persona: number;
  id_organizacion: number;
  id_rol: number;
  email: string;
  nombre_usuario: string;
}

interface AuthContextType {
  usuario: UsuarioActual | null;
  token: string | null;
  cargando: boolean;
  iniciarSesion: (email: string, contrasena: string) => Promise<UsuarioActual>;
  cerrarSesion: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const API_URL = "http://127.0.0.1:8000";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<UsuarioActual | null>(null);
  const [token, setToken] = useState<string | null>(
    localStorage.getItem("flowos_token"),
  );
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    const cargarUsuario = async () => {
      const tokenGuardado = localStorage.getItem("flowos_token");

      if (!tokenGuardado) {
        setCargando(false);
        return;
      }

      try {
        const respuesta = await fetch(`${API_URL}/auth/me`, {
          headers: {
            Authorization: `Bearer ${tokenGuardado}`,
          },
        });

        if (!respuesta.ok) {
          throw new Error("Sesión inválida");
        }

        const datos = await respuesta.json();

        setToken(tokenGuardado);
        setUsuario(datos);
      } catch {
        localStorage.removeItem("flowos_token");
        setToken(null);
        setUsuario(null);
      } finally {
        setCargando(false);
      }
    };

    cargarUsuario();
  }, []);

  const iniciarSesion = async (
    email: string,
    contrasena: string,
  ): Promise<UsuarioActual> => {
    const respuesta = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email,
        contrasena,
      }),
    });

    if (!respuesta.ok) {
      let mensaje = "No fue posible iniciar sesión.";

      try {
        const error = await respuesta.json();

        if (error.detail) {
          mensaje = error.detail;
        }
      } catch {
        // Se conserva el mensaje por defecto.
      }

      throw new Error(mensaje);
    }

    const datos = await respuesta.json();

    localStorage.setItem("flowos_token", datos.access_token);
    setToken(datos.access_token);

    const respuestaUsuario = await fetch(`${API_URL}/auth/me`, {
      headers: {
        Authorization: `Bearer ${datos.access_token}`,
      },
    });

    if (!respuestaUsuario.ok) {
      localStorage.removeItem("flowos_token");
      setToken(null);
      throw new Error("No fue posible obtener la información del usuario.");
    }

    const datosUsuario = await respuestaUsuario.json();

    setUsuario(datosUsuario);
    return datosUsuario;
  };

  const cerrarSesion = () => {
    localStorage.removeItem("flowos_token");
    setToken(null);
    setUsuario(null);
  };

  return (
    <AuthContext.Provider
      value={{
        usuario,
        token,
        cargando,
        iniciarSesion,
        cerrarSesion,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const contexto = useContext(AuthContext);

  if (!contexto) {
    throw new Error("useAuth debe utilizarse dentro de AuthProvider.");
  }

  return contexto;
}
