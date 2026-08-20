import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  apiRequest,
  clearTokens,
  saveTokens,
} from "./api";
import { authClient } from "./auth";
import { AuthContext } from "./authContextInstance";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadUser = useCallback(async () => {
    try {
      // 1. Check Neon Auth session via authClient
      let sessionToken = null;
      try {
        const sessionResult = await authClient.getSession();
        const sessionData = sessionResult?.data || sessionResult;
        sessionToken =
          sessionData?.session?.token ||
          sessionData?.token ||
          sessionData?.session?.id;
      } catch {
        // authClient.getSession() returned unauthenticated
      }

      if (sessionToken) {
        saveTokens(sessionToken);
        const syncedUser = await apiRequest(
          "/auth/sync-session",
          {
            method: "POST",
            body: JSON.stringify({ session_token: sessionToken }),
          },
          false,
        );
        setUser(syncedUser);
        return syncedUser;
      }

      // 2. Fallback: check if we have an existing local token
      const localToken = localStorage.getItem("skillbeacon_access_token");
      if (!localToken) {
        setUser(null);
        return null;
      }

      const currentUser = await apiRequest("/auth/me");
      setUser(currentUser);
      return currentUser;
    } catch {
      clearTokens();
      setUser(null);
      return null;
    }
  }, []);

  useEffect(() => {
    loadUser().finally(() => setLoading(false));
  }, [loadUser]);

  const login = useCallback(
    async (email, password) => {
      const res = await authClient.signIn.email({
        email,
        password,
      });

      if (res?.error) {
        throw new Error(res.error.message || "Failed to log in");
      }

      let sessionToken =
        res?.data?.session?.token ||
        res?.session?.token ||
        res?.data?.token ||
        res?.token;

      if (!sessionToken) {
        const sessionResult = await authClient.getSession();
        const sessionData = sessionResult?.data || sessionResult;
        sessionToken = sessionData?.session?.token;
      }

      if (sessionToken) {
        saveTokens(sessionToken);
        const syncedUser = await apiRequest(
          "/auth/sync-session",
          {
            method: "POST",
            body: JSON.stringify({ session_token: sessionToken }),
          },
          false,
        );
        setUser(syncedUser);
        return syncedUser;
      }

      return loadUser();
    },
    [loadUser],
  );

  const register = useCallback(
    async (email, password, role = "student") => {
      const res = await authClient.signUp.email({
        email,
        password,
        name: email.split("@")[0],
      });

      if (res?.error) {
        throw new Error(res.error.message || "Failed to create account");
      }

      let sessionToken =
        res?.data?.session?.token ||
        res?.session?.token ||
        res?.data?.token ||
        res?.token;

      if (!sessionToken) {
        const sessionResult = await authClient.getSession();
        const sessionData = sessionResult?.data || sessionResult;
        sessionToken = sessionData?.session?.token;
      }

      if (sessionToken) {
        saveTokens(sessionToken);
        const syncedUser = await apiRequest(
          "/auth/sync-session",
          {
            method: "POST",
            body: JSON.stringify({
              session_token: sessionToken,
              role,
            }),
          },
          false,
        );
        setUser(syncedUser);
        return syncedUser;
      }

      // If session token not immediately returned, try signing in to retrieve session
      try {
        const loginRes = await authClient.signIn.email({ email, password });
        let loginToken =
          loginRes?.data?.session?.token ||
          loginRes?.session?.token ||
          loginRes?.data?.token ||
          loginRes?.token;

        if (!loginToken) {
          const sessionResult = await authClient.getSession();
          const sessionData = sessionResult?.data || sessionResult;
          loginToken = sessionData?.session?.token;
        }

        if (loginToken) {
          saveTokens(loginToken);
          const syncedUser = await apiRequest(
            "/auth/sync-session",
            {
              method: "POST",
              body: JSON.stringify({
                session_token: loginToken,
                role,
              }),
            },
            false,
          );
          setUser(syncedUser);
          return syncedUser;
        }
      } catch {
        // Fall back to loadUser
      }

      return loadUser();
    },
    [loadUser],
  );

  const logout = useCallback(async () => {
    try {
      await authClient.signOut();
    } catch {
      // continue logout cleanup
    } finally {
      clearTokens();
      setUser(null);
    }
  }, []);

  const value = useMemo(
    () => ({
      user,
      loading,
      login,
      register,
      logout,
      loadUser,
    }),
    [user, loading, login, register, logout, loadUser],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}