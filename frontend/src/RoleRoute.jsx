import {
  Navigate,
} from "react-router";

import {
  useAuth,
} from "./AuthContext";


export default function RoleRoute({
  roles,
  children,
}) {
  const { user } = useAuth();


  if (!user) {
    return (
      <Navigate
        to="/login"
        replace
      />
    );
  }


  if (
    !roles.includes(
      user.role
    )
  ) {
    return (
      <Navigate
        to="/app/dashboard"
        replace
      />
    );
  }


  return children;
}