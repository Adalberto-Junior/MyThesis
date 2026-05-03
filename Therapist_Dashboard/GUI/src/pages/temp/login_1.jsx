import React from "react";
import '../App.css'; // Importando o CSS tradicional

export default function LoginForm () {
  return (
    <div className="container mx-auto max-w-md mt-10 p-5 bg-gray-100">
      <h2 className="text-2xl font-bold text-center mb-5">Login</h2>
      <input type="text" placeholder="Nome de usuário" className="w-full bg-white text-black p-2 border border-gray-300 rounded-md mb-4" />
      <input type="password" placeholder="Senha" className="w-full bg-white text-black p-2 border border-gray-300 rounded-md mb-4" />
      <button className="w-full bg-green-500 text-white p-2 rounded-md hover:bg-green-600">Entrar</button>
    </div>
  );
};


