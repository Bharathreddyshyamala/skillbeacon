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
import Mentorships from "./pages/Mentorships";
import Challenges from "./pages/Challenges";
import ChallengeSubmissions from "./pages/ChallengeSubmissions";
import ManageChallenges from "./pages/ManageChallenges";
import EmployerChallengeSubmissions from "./pages/EmployerChallengeSubmissions";
import Notifications from "./pages/Notifications";
import RoleRoute from "./RoleRoute";

import AdminDashboard
  from "./pages/admin/AdminDashboard";

import AdminUsers
  from "./pages/admin/AdminUsers";

import AdminContent
  from "./pages/admin/AdminContent";

import AdminAuditLogs
  from "./pages/admin/AdminAuditLogs";

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
          <Route path="/app/mentorships" element={<Mentorships />}/>
          <Route path="/app/challenges" element={<Challenges />}/>
          <Route path="/app/challenge-submissions" element={<ChallengeSubmissions />}/>
          <Route path="/app/challenges/manage" element={<ManageChallenges />}/>
          <Route path="/app/challenges/:challengeId/submissions" element={<EmployerChallengeSubmissions />}/>
          <Route path="/app/notifications" element={<Notifications />}/>
          <Route path="/app/admin" element={<RoleRoute roles={["admin"]}> <AdminDashboard /> </RoleRoute>}/>
          <Route path="/app/admin/users" element={<RoleRoute roles={["admin"]}> <AdminUsers /> </RoleRoute>}/>
          <Route path="/app/admin/content" element={<RoleRoute roles={["admin"]}> <AdminContent /> </RoleRoute>}/>
          <Route path="/app/admin/audit-logs" element={<RoleRoute roles={["admin"]}> <AdminAuditLogs /> </RoleRoute>}/>
        </Route>
      </Route>


    </Routes>
  );
}
