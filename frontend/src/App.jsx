import { Navigate, Route, Routes } from "react-router";

import ProtectedRoute from "./ProtectedRoute";
import Layout from "./Layout";
import Dashboard from "./pages/Dashboard";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Profile from "./pages/Profile";
import Register from "./pages/Register";
import Skills from "./pages/Skills";
import Verifications from "./pages/Verifications";
import Opportunities from "./pages/Opportunities";
import ManageOpportunities from "./pages/ManageOpportunities";
export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      
      

      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/app" element={<Navigate to="/app/dashboard" replace />} />
          <Route path="/app/dashboard" element={<Dashboard />} />
          <Route path="/app/profile" element={<Profile />} />
          <Route path="/app/skills" element={<Skills />} />
          <Route path="/app/verifications" element={<Verifications />}/>
          <Route path="/app/opportunities" element={<Opportunities />} />
          <Route path="/app/opportunities/manage" element={<ManageOpportunities />}/>

        </Route>
      </Route>

      {/*<Route path="*" element={<Navigate to="/" replace />} />*/}
    </Routes>
  );
}
