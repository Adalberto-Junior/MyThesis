
import React from "react";
import api from "../../../api";
import { useForm } from "react-hook-form";
import { ErrorMessage } from "@hookform/error-message";
import "react-phone-number-input/style.css";
import PhoneInput from "react-phone-number-input";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "../../../components/ui/card";
import { Button } from "../../../components/ui/button";
import { UserPlus, XCircle } from "lucide-react";

export default function FloatingForm({ onClose }) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  const onSubmit = async (data) => {
    try {
      await api.post("/utente/", data);
      alert("Utente adicionado com sucesso!");
      window.location.reload();
    } catch (error) {
      console.error("Erro ao adicionar utente:", error);
      alert("Erro ao adicionar utente. Por favor, tenta novamente.");
    }
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm z-50">
      <Card className="w-full max-w-lg max-h-[90vh] overflow-y-auto shadow-lg dark:bg-zinc-800">
        <CardHeader>
          <CardTitle className="text-2xl font-bold text-center dark:text-white">
            Adicionar Utente
          </CardTitle>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {/* Nome */}
            <div>
              <input
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 dark:bg-zinc-700 dark:border-zinc-600 dark:text-white"
                type="text"
                placeholder="Nome"
                {...register("name", { required: "Nome é obrigatório." })}
              />
              <ErrorMessage
                errors={errors}
                name="name"
                render={({ message }) => <span className="text-red-500 text-sm">{message}</span>}
              />
            </div>

            {/* Email */}
            <div>
              <input
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 dark:bg-zinc-700 dark:border-zinc-600 dark:text-white"
                type="email"
                placeholder="Email"
                {...register("email", {
                  required: "Email é obrigatório.",
                  pattern: {
                    value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                    message: "Digite um email válido.",
                  },
                })}
              />
              <ErrorMessage
                errors={errors}
                name="email"
                render={({ message }) => <span className="text-red-500 text-sm">{message}</span>}
              />
            </div>

            {/* Nº Saúde */}
            <div>
              <input
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 dark:bg-zinc-700 dark:border-zinc-600 dark:text-white"
                type="number"
                placeholder="Número de Saúde do Utente"
                {...register("health_user_number", {
                  required: "Número de utente é obrigatório.",
                  minLength: {
                    value: 9,
                    message: "O número do Utente deve ter pelo menos 9 números.",
                  },
                })}
              />
              <ErrorMessage
                errors={errors}
                name="health_user_number"
                render={({ message }) => <span className="text-red-500 text-sm">{message}</span>}
              />
            </div>

            {/* Telemóvel */}
            <div>
              <PhoneInput
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 dark:bg-zinc-700 dark:border-zinc-600 dark:text-white"
                placeholder="Telemóvel"
                defaultCountry="PT"
                international
                {...register("health_user_cellphone")}
              />
              <ErrorMessage
                errors={errors}
                name="health_user_cellphone"
                render={({ message }) => <span className="text-red-500 text-sm">{message}</span>}
              />
            </div>

            {/* Morada */}
            <div>
              <input
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 dark:bg-zinc-700 dark:border-zinc-600 dark:text-white"
                type="text"
                placeholder="Morada"
                {...register("health_user_address")}
              />
            </div>

            {/* Condição de Saúde */}
            <div>
              <input
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 dark:bg-zinc-700 dark:border-zinc-600 dark:text-white"
                type="text"
                placeholder="Condição de Saúde"
                {...register("medical_condition")}
              />
            </div>

            {/* Data de Nascimento */}
            <div>
              <label htmlFor="date_birth" className="block text-sm font-medium mb-1 dark:text-white">
                Data de Nascimento
              </label>
              <input
                type="date"
                id="date_birth"
                {...register("date_birth", { required: "Data de nascimento é obrigatória." })}
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 dark:bg-zinc-700 dark:border-zinc-600 dark:text-white"
              />
              <ErrorMessage
                errors={errors}
                name="date_birth"
                render={({ message }) => <span className="text-red-500 text-sm">{message}</span>}
              />
            </div>

            {/* Observação */}
            <div>
              <textarea
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 dark:bg-zinc-700 dark:border-zinc-600 dark:text-white"
                placeholder="Observações"
                {...register("observation")}
              />
            </div>

            <Button type="submit" className="w-full flex items-center justify-center gap-2">
              <UserPlus size={18} /> Adicionar Utente
            </Button>
          </form>
        </CardContent>

        <CardFooter className="flex justify-center">
          <Button
            onClick={onClose}
            variant="outline"
            className="w-full flex items-center justify-center gap-2"
          >
            <XCircle size={18} /> Fechar
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
