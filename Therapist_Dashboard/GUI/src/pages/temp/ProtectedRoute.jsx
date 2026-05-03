import { Navigate } from "react-router-dom";

const isAuthenticated = () => {
    return localStorage.getItem('token') !== null;
  };
  
  export default function ProtectedRoute({ element }) {
  return isAuthenticated() ? element : <Navigate to="/login" />;
};

