import { createContext, useContext, useState, useEffect } from "react";
import api from "../../../api";

const UserContext = createContext();

export const UserProvider = ({ children }) => {
  const [user, setUsuario] = useState(null);

  useEffect(() => {
    fetch("/api/usuarioAtual") 
      .then((res) => res.json())
      .then((data) => setUsuario(data));
  }, []);

  return (
    <UserContext.Provider value={user}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => useContext(UserContext);

