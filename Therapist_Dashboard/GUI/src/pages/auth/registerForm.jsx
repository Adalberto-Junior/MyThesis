
import React from 'react';
import { useForm } from "react-hook-form";
import { ErrorMessage } from "@hookform/error-message";
import api from "../../api";
import { useNavigate } from "react-router-dom";
import '../../App.css';

export default function RegisterForm () {
  const { register, handleSubmit,watch, formState: { errors } } = useForm();
  const navigate = useNavigate();

  // O método watch monitora o valor do campo "password"
  const senha = watch("password", "");
  
  const onSubmit = async (data) => {
    try {
      
      
      const response = await api.post("/auth/register", data);

      
      alert("Utilizador registado com sucesso!");
      navigate("/login"); 

    } catch (error) {
      console.error("Erro ao registrar:", error);

      if (error.response && error.response.status === 409) {
        alert("Nome de utilizador já existe. Tente outro.");
      } else {
        alert("Erro ao registrar o utilizador. Tente novamente.");
      }
    }
  };
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-zinc-900 px-4">
      <div className="w-full max-w-md bg-white dark:bg-zinc-800 shadow-md rounded-lg p-6">
        <h2 className="text-2xl font-semibold text-center text-black dark:text-white mb-6">Registar</h2>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            {/* <label htmlFor="name">Nome do Utilizador</label> */}
            <input
              className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-zinc-700 dark:border-zinc-600 dark:text-white"
              type="text"
              id="name"
              name="name"
              placeholder="User Name"
              {...register("name", {
                required: "O Nome do Utilizador é obrigatório.",
                maxLength: {
                  value: 50,
                  message: "O campo precisa ter no máximo 50 caracteres."
                }
              })}
              
            />
            <ErrorMessage errors={errors} name="name"  render={({ message }) => <span className="error-message">{message}</span>} />
          </div>
          <div>
            {/* <label htmlFor="email">Email</label> */}
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
            
            <ErrorMessage errors={errors} name="email"  render={({ message }) => <span className="error-message">{message}</span>} />
          </div>
          <div>
            {/* <label htmlFor="password">Palavra-Passe</label> */}
            <input
              className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-zinc-700 dark:border-zinc-600 dark:text-white"
              type="password"
              id="password"
              name="password"
              placeholder="Password"
              {...register("password", {
                required: "Palavra-passe é obrigatória.",
                minLength: {
                  value: 8,
                  message: "A palavra-passe deve ter pelo menos 8 caracteres."
                },
                pattern: {
                  value: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$/,
                  message: "A senha deve conter pelo menos uma letra maiúscula, uma letra minúscula, um número e um caractere especial."
                }
              })}
            />
            <ErrorMessage errors={errors} name="password"  render={({ message }) => <span className="error-message">{message}</span>}/>
          </div>
          <div>
            {/* <label htmlFor="confirmPassword">Confirmar Palavra-Passe</label> */}
            <input
              className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-zinc-700 dark:border-zinc-600 dark:text-white"
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              placeholder="Confirm Password"
              {...register("confirmPassword", {
                required: "A confirmação da palavra-passe é obrigatória.",
                validate: (value) =>
                  value === senha || "As palavras-passes não correspondem."
              })}
            />
            <ErrorMessage errors={errors} name="confirmPassword" render={({ message }) => (<span className="error-message">{message}</span> )}/>
          </div>
          <div>
            {/* <label htmlFor="profession">Profissão</label> */}
            <input
              className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-zinc-700 dark:border-zinc-600 dark:text-white"
              type="text"
              id="profession"
              name="profession"
              placeholder="Profession"
              {...register("profession", {
                required: "A profissão é obrigatória.",
                maxLength: {
                  value: 50,
                  message: "O campo precisa ter no máximo 50 caracteres."
                }
              })}
              
            />
            <ErrorMessage errors={errors} name="profession"  render={({ message }) => <span className="error-message">{message}</span>} />
          </div>
          <div>
            <label htmlFor="date_birth">Data de Nascimento</label>
            <input
              className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-zinc-700 dark:border-zinc-600 dark:text-white"
              type="date"
              id="date_birth"
              name="date_birth"
              {...register("date_birth", {
                required: "Data de nascimento é obrigatória."
              })}

            />
            <ErrorMessage errors={errors} name="date_birth"  render={({ message }) => <span className="error-message">{message}</span>} />
          </div>
          <button type="submit" className="w-99 bg-green-500 text-white py-2 px-3 rounded mr-2 hover:bg-green-600">Registar</button>
          <p className="text-black bg-white p-2">Já tem conta? <a href="/">Iniciar Sessão</a></p>
        </form>
      </div>
    </div>
  );
};


