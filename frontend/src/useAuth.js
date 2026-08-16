import { useContext } from "react";
import { AuthContext } from "./authContextInstance";

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) {
    throw new Error("useAuth must be inside AuthProvider");
  }
  return value;
}
