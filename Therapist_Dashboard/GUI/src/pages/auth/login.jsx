
import React from 'react';
import { useForm } from "react-hook-form";
import { ErrorMessage } from "@hookform/error-message";
import api from "../../api"; 
import { useNavigate } from "react-router-dom";
import '../../App.css';

export default function LoginForm ({ setIsAuth }) {
  const { register, handleSubmit, formState: { errors } } = useForm();
  const navigate = useNavigate();

  const onSubmit = async (data) => {
    try {
      const response = await api.post("/auth/login", data);
      localStorage.setItem("token", response.data.token);

      setIsAuth(true);
      navigate("/"); 
    } catch (error) {
      console.error("Login failed:", error);
        if (error.response && error.response.status === 401) {
            alert("Nome de utilizador ou senha inválidos. Tente novamente.");
        } else {
            alert("Erro ao fazer login. Tente novamente.");
        }
    }
  }; 

  return (
    // <div className='container' >
    <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-zinc-900 px-4">
      <div className="w-full max-w-md bg-white dark:bg-zinc-800 shadow-md rounded-lg p-6">
        <h2 className="text-2xl font-semibold text-center text-black dark:text-white mb-6">Login</h2>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            {/* <label className='p-2' htmlFor="email">Email</label> */}
            <input
              className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-zinc-700 dark:border-zinc-600 dark:text-white"
              type="email"
              id="email"
              name="email"
              placeholder="Email"
              {...register("email", {
                  required: "Email é obrigatório.",
                  pattern: {
                    value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                    message: "Digite um email válido."
                  }
              })}
            />
            <ErrorMessage errors={errors} name="email" render={({ message }) => <p>{message}</p>} />
          </div>
          <div>
            {/* <label htmlFor="password">Password</label> */}
            <input
              className="w-full p-5 px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-zinc-700 dark:border-zinc-600 dark:text-white"
              type="password"
              id="password"
              name="password"
              placeholder="Password"
              {...register("password", { required: "Password is required" })}
            />
            <ErrorMessage errors={errors} name="password" render={({ message }) => <p>{message}</p>} />
          </div>
          <button type="submit" className="w-99 bg-green-500 text-white py-2 px-3 rounded mr-2 hover:bg-green-600">Entrar</button>
          <div className="mt-4 text-center">
            <p>Não tem uma conta? <a href="/register" className="text-blue-500">Registrar</a></p>
          </div>
        </form>
      </div>
    </div>
  );
};
