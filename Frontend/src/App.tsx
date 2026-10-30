import { Navigate, Outlet, Route, Routes } from "react-router-dom";

import MainLayout from "./layouts/MainLayout";

import Dashboard from "./pages/Dashboard/Dashboard";
import Proyectos from "./pages/Proyectos/Proyectos";
import Personas from "./pages/Personas/Personas";
import Equipos from "./pages/Equipos/Equipos";
import Tareas from "./pages/Tareas/Tareas";
import Optima from "./pages/Optima/Optima";
import Login from "./pages/Login/Login";
import Usuarios from "./pages/Usuario/Usuarios";
import RegistroEmpleado from "./pages/Registro/Registro_Empleado";
import RecuperarContrasena from "./pages/RecuperarContrasena/RecuperarContrasena";
import Organizaciones from "./pages/Organizaciones/Organizaciones";
import MiPanel from "./pages/MiPanel/MiPanel";
import MisTareas from "./pages/MisTareas/MisTareas";
import MisProyectos from "./pages/MisProyectos/MisProyectos";
import MiEquipo from "./pages/MiEquipo/MiEquipo";
import MisHabilidades from "./pages/MisHabilidades/MisHabilidades";
import Chat from "./pages/Chat/Chat";
import Habilidades from "./pages/Habilidad/Habilidades";

import { useAuth } from "./context/AuthContext";

interface RutaPorRolProps {
  rolesPermitidos: number[];
}

function RutaProtegida() {
  const { usuario, cargando } = useAuth();

  if (cargando) {
    return <div className="login-loading">Cargando FLOWOS...</div>;
  }

  if (!usuario) {
    return <Navigate to="/login" replace />;
  }

  return <MainLayout />;
}

function RutaPorRol({ rolesPermitidos }: RutaPorRolProps) {
  const { usuario } = useAuth();

  if (!usuario) {
    return <Navigate to="/login" replace />;
  }

  if (!rolesPermitidos.includes(usuario.id_rol)) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}

function App() {
  return (
    <Routes>
      {/* ========== RUTAS PÚBLICAS ========== */}
      <Route path="/login" element={<Login />} />
      <Route path="/registro" element={<RegistroEmpleado />} />
      <Route path="/recuperar-contrasena" element={<RecuperarContrasena />} />

      {/* ========== ÁREA PROTEGIDA ========== */}
      <Route path="/" element={<RutaProtegida />}>
        <Route index element={<Navigate to="/dashboard" replace />} />

        <Route path="dashboard" element={<Dashboard />} />

        <Route element={<RutaPorRol rolesPermitidos={[1]} />}>
          <Route path="usuarios" element={<Usuarios />} />
        </Route>

        <Route element={<RutaPorRol rolesPermitidos={[1, 2, 3, 4]} />}>
          <Route path="proyectos" element={<Proyectos />} />
        </Route>

        <Route element={<RutaPorRol rolesPermitidos={[1, 2, 3, 4]} />}>
          <Route path="personas" element={<Personas />} />
        </Route>

        <Route element={<RutaPorRol rolesPermitidos={[1, 2, 3, 4]} />}>
          <Route path="equipos" element={<Equipos />} />
        </Route>

        <Route element={<RutaPorRol rolesPermitidos={[1, 2, 3, 4]} />}>
          <Route path="tareas" element={<Tareas />} />
        </Route>

        <Route element={<RutaPorRol rolesPermitidos={[1]} />}>
          <Route path="optima" element={<Optima />} />
        </Route>

        <Route element={<RutaPorRol rolesPermitidos={[5]} />}>
          <Route path="organizaciones" element={<Organizaciones />} />
        </Route>

        <Route element={<RutaPorRol rolesPermitidos={[4]} />}>
          <Route path="mi-panel" element={<MiPanel />} />
        </Route>

        <Route element={<RutaPorRol rolesPermitidos={[4]} />}>
          <Route path="mis-tareas" element={<MisTareas />} />
        </Route>

        <Route element={<RutaPorRol rolesPermitidos={[4]} />}>
          <Route path="mis-proyectos" element={<MisProyectos />} />
        </Route>

        <Route element={<RutaPorRol rolesPermitidos={[4]} />}>
          <Route path="mi-equipo" element={<MiEquipo />} />
        </Route>

        <Route element={<RutaPorRol rolesPermitidos={[4]} />}>
          <Route path="mis-habilidades" element={<MisHabilidades />} />
        </Route>

        <Route element={<RutaPorRol rolesPermitidos={[1, 2, 3, 4]} />}>
          <Route path="chat" element={<Chat />} />
        </Route>

        <Route element={<RutaPorRol rolesPermitidos={[1, 3]} />}>
          <Route path="habilidades" element={<Habilidades />} />
        </Route>

        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Route>

      {/* Fallback global */}
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}
export default App;
