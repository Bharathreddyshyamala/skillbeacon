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
import Applications from "./pages/Applications";
import OpportunityApplicants from "./pages/OpportunityApplicants";
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
          <Route path="/app/applications" element={<Applications />}/>
          <Route path="/app/opportunities/:opportunityId/applicants" element={<OpportunityApplicants />}/>

        </Route>
      </Route>

      {/*<Route path="*" element={<Navigate to="/" replace />} />*/}
    </Routes>
  );
}
