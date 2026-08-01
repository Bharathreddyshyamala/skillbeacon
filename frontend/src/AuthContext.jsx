import {
    createContext,
    useCallback,
    useContext,
    useEffect,
    useMemo,
    useState,
  } from "react";
  
  import {
    apiRequest,
    clearTokens,
    getRefreshToken,
    saveTokens,
  } from "./api";
  
  const AuthContext = createContext(null);
  
  export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
  
    const loadUser = useCallback(async () => {
      try {
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
  
    const login = useCallback(async (email, password) => {
      const data = await apiRequest(
        "/auth/login",
        {
          method: "POST",
          body: JSON.stringify({ email, password }),
        },
        false,
      );
      saveTokens(data.access_token, data.refresh_token);
      setUser(data.user);
    }, []);
  
    const register = useCallback(
      async (email, password, role) => {
        await apiRequest(
          "/auth/register",
          {
            method: "POST",
            body: JSON.stringify({ email, password, role }),
          },
          false,
        );
        await login(email, password);
      },
      [login],
    );
  
    const logout = useCallback(async () => {
      const refreshToken = getRefreshToken();
      try {
        if (refreshToken) {
          await apiRequest(
            "/auth/logout",
            {
              method: "POST",
              body: JSON.stringify({ refresh_token: refreshToken }),
            },
            false,
          );
        }
      } finally {
        clearTokens();
        setUser(null);
      }
    }, []);
  
    const value = useMemo(
      () => ({ user, loading, login, register, logout }),
      [user, loading, login, register, logout],
    );
  
    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
  }
  
  export function useAuth() {
    const value = useContext(AuthContext);
    if (!value) throw new Error("useAuth must be inside AuthProvider");
    return value;
  }
  