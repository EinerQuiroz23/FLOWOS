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
      {/* =========================================
            AUTENTICACIÓN
        ========================================= */}

      <Route path="/login" element={<Login />} />

      {/* =========================================
            ÁREA PROTEGIDA
        ========================================= */}

      <Route path="/" element={<RutaProtegida />}>
        <Route index element={<Navigate to="/dashboard" replace />} />

        {/* =========================================
              DASHBOARD
              Todos los usuarios autenticados
          ========================================= */}

        <Route path="dashboard" element={<Dashboard />} />

        <Route element={<RutaPorRol rolesPermitidos={[1]} />}>
          <Route path="usuarios" element={<Usuarios />} />
        </Route>

        {/* =========================================
              PROYECTOS
              ADMIN + LÍDER + SECRETARIO + EMPLEADO
          ========================================= */}

        <Route element={<RutaPorRol rolesPermitidos={[1, 2, 3, 4]} />}>
          <Route path="proyectos" element={<Proyectos />} />
        </Route>

        {/* =========================================
              PERSONAS
              Todos los usuarios autenticados
          ========================================= */}

        <Route element={<RutaPorRol rolesPermitidos={[1, 2, 3, 4]} />}>
          <Route path="personas" element={<Personas />} />
        </Route>

        {/* =========================================
              EQUIPOS
              ADMIN + LÍDER + SECRETARIO + EMPLEADO
          ========================================= */}

        <Route element={<RutaPorRol rolesPermitidos={[1, 2, 3, 4]} />}>
          <Route path="equipos" element={<Equipos />} />
        </Route>

        {/* =========================================
              TAREAS
              ADMIN + LÍDER + SECRETARIO + EMPLEADO
          ========================================= */}

        <Route element={<RutaPorRol rolesPermitidos={[1, 2, 3, 4]} />}>
          <Route path="tareas" element={<Tareas />} />
        </Route>

        {/* =========================================
              OPTIMA
              SOLO ADMIN
          ========================================= */}

        <Route element={<RutaPorRol rolesPermitidos={[1]} />}>
          <Route path="optima" element={<Optima />} />
        </Route>

        {/* =========================================
              RUTA NO ENCONTRADA
          ========================================= */}

        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Route>

      {/* =========================================
            RUTA GLOBAL NO ENCONTRADA
        ========================================= */}

      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

export default App;
