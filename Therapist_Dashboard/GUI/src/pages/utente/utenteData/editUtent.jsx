
import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { Save, X, Loader2 } from "lucide-react";
import api from "../../../api";
import 'react-phone-number-input/style.css';
import PhoneInput from 'react-phone-number-input';

export default function EditUtente() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const { register, handleSubmit, setValue, watch, formState: { errors } } = useForm({
    defaultValues: {
      name: "",
      email: "",
      health_user_number: "",
      address: "",
      medical_condition: "",
      cellphone: "",
      observation: "",
      date_of_birth: "",
    }
  });

  useEffect(() => {
    async function fetchUtente() {
      try {
        const res = await api.get(`/utente/informacao/${id}`);
        const data = res.data;
        Object.keys(data).forEach((key) => {
          if (data[key] !== undefined) setValue(key, data[key]);
        });
      } catch (err) {
        setError("Erro ao carregar os dados do utente.");
      } finally {
        setLoading(false);
      }
    }

    fetchUtente();
  }, [id, setValue]);

  const onSubmit = async (data) => {
    try {
      await api.put(`/utente/informacao/${id}`, data);
      alert("Utente atualizado com sucesso!");
      navigate(`/utente/${id}/informacao`);
    } catch (err) {
      console.error(err);
      alert("Erro ao atualizar o utente.");
    }
  };

  if (loading) {
      return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 dark:bg-zinc-900">
          <Loader2 className="animate-spin w-10 h-10 text-primary mb-3" />
          <p className="text-lg font-semibold dark:text-white">Carregando os dados...</p>
        </div>
      );
    }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-zinc-900">
        <p className="text-lg font-semibold text-red-500">Erro: {error}</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-zinc-900 px-4 py-8">
      <div className="w-full max-w-2xl bg-white dark:bg-zinc-800 shadow-xl rounded-2xl p-6">
        <h2 className="text-2xl font-bold text-center mb-6 text-gray-900 dark:text-white">
          Editar Utente
        </h2>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Nome</label>
            <input
              type="text"
              {...register("name", { required: "O nome é obrigatório" })}
              className="w-full border rounded-lg p-2 focus:ring-2 focus:ring-blue-500 dark:bg-zinc-700 dark:text-white"
            />
            {errors.name && <p className="text-red-500 text-xs mt-1">{errors.name.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Email</label>
            <input
              type="email"
              {...register("email", {
                required: "O email é obrigatório",
                pattern: { value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, message: "Email inválido" }
              })}
              className="w-full border rounded-lg p-2 focus:ring-2 focus:ring-blue-500 dark:bg-zinc-700 dark:text-white"
            />
            {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Número de Utente</label>
            <input
              type="number"
              {...register("health_user_number")}
              className="w-full border rounded-lg p-2 dark:bg-zinc-700 dark:text-white"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Morada</label>
            <input
              type="text"
              {...register("address")}
              className="w-full border rounded-lg p-2 dark:bg-zinc-700 dark:text-white"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Condição de Saúde</label>
            <input
              type="text"
              {...register("medical_condition")}
              className="w-full border rounded-lg p-2 dark:bg-zinc-700 dark:text-white"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Telemóvel</label>
            <PhoneInput
              defaultCountry="PT"
              international
              value={watch("cellphone")}
              onChange={(value) => setValue("cellphone", value)}
              className="w-full border rounded-lg p-2 dark:bg-zinc-700 dark:text-white"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Observação</label>
            <textarea
              rows={3}
              {...register("observation")}
              className="w-full border rounded-lg p-2 dark:bg-zinc-700 dark:text-white"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Data de Nascimento</label>
            <input
              type="date"
              {...register("date_of_birth")}
              className="w-full border rounded-lg p-2 dark:bg-zinc-700 dark:text-white"
            />
          </div>

          <div className="flex justify-between pt-4 border-t dark:border-zinc-700">
            <button
              type="submit"
              className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded shadow-md transition"
            >
              <Save className="w-4 h-4" /> Salvar Alterações
            </button>

            <button
              type="button"
              onClick={() => navigate(`/utente/${id}/informacao`)}
              className="flex items-center gap-2 bg-amber-500 hover:bg-amber-600 text-white px-4 py-2 rounded shadow-md transition"
            >
              <X className="w-4 h-4" /> Cancelar
            </button>

            
          </div>
        </form>
      </div>
    </div>
  );
}
