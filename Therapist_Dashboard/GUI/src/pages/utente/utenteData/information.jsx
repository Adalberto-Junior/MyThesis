import React, { useEffect, useState } from "react";
import api from "../../../api.jsx";
import { useNavigate, useParams } from "react-router-dom";
import { useForm, Controller } from "react-hook-form";
import { MultiSelect } from "primereact/multiselect";
import { Pencil, Trash2, Plus, FileText, ArrowLeft, User, Loader2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

import "primereact/resources/themes/lara-light-blue/theme.css";
import "primereact/resources/primereact.min.css";
import "primeicons/primeicons.css";

export default function HealthUserInformation() {
  const [utente, setUtente] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const { id } = useParams();

  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const { register, handleSubmit, control } = useForm();
  const [tiposSelecionados, setTiposSelecionados] = useState([]);
  const [comentariosAnalises, setComentariosAnalises] = useState({});

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get(`/utente/informacao/${id}`);
        setUtente(response.data);
      } catch (error) {
        setError(error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  function calcularIdade(dataNascimento) {
    if (!dataNascimento) return "N/A";
    const nascimento = new Date(dataNascimento);
    const hoje = new Date();

    let idade = hoje.getFullYear() - nascimento.getFullYear();
    const m = hoje.getMonth() - nascimento.getMonth();
    if (m < 0 || (m === 0 && hoje.getDate() < nascimento.getDate())) idade--;

    if (nascimento.getFullYear() === hoje.getFullYear()) {
      return m === 0 ? `${idade} D` : `${idade} M`;
    }
    return `${idade} A`;
  }

  const handleEdit = () => navigate(`/utente/${id}/editar`);
  const handleSeeReport = () => navigate(`/utente/${id}/relatorio`);

  const handleDelete = async () => {
    if (!window.confirm("Tem a certeza que deseja eliminar este utente?")) return;
    try {
      await api.delete(`/utente/informacao/${id}`);
      navigate("/");
    } catch (error) {
      console.error("Erro ao eliminar utente:", error);
    }
  };

  const onSubmit = async (data) => {
    try {
      const analises = tiposSelecionados.map((tipo) => ({
        tipo,
        resultado: comentariosAnalises[tipo] || "",
      }));

      const payload = {
        ...data,
        analises,
        utente_id: id,
        status: data.status,
        views: 0,
        created_at: new Date().toISOString(),
      };

      await api.post(`/utente/${id}/relatorio/`, payload);
      alert("Relatório enviado com sucesso!");
      setMostrarFormulario(false);
      window.location.reload();
    } catch (error) {
      console.error("Erro ao enviar relatório:", error);
      alert("Erro ao enviar relatório.");
    }
  };

  if (loading)
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-zinc-900">
        <Loader2 className="animate-spin w-10 h-10 text-primary mb-3" />
        <p className="text-lg font-semibold dark:text-white">
          Carregando dados do utente...
        </p>
      </div>
    );

  if (error)
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-zinc-900">
        <p className="text-lg font-semibold text-red-500">
          Erro: {error.message}
        </p>
      </div>
    );

  const labels = {
    name: "Nome",
    date_of_birth: "Data de Nascimento",
    observation: "Observação",
    health_user_number: "Nº Saúde",
    address: "Morada",
    medical_condition: "Condição de Saúde",
    cellphone: "Telemóvel",
    email: "Email",
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-zinc-900 px-4 py-8 transition-colors duration-300">
      {/* Barra superior */}
      <div className="flex justify-between items-center max-w-5xl mx-auto mb-6">
        <button
          onClick={() => navigate("/")}
          className="flex items-center gap-2 px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700 transition shadow-md"
        >
          <ArrowLeft className="w-5 h-5" /> Voltar
        </button>

        <button
          onClick={handleSeeReport}
          className="flex items-center gap-2 px-4 py-2 rounded bg-gray-700 text-white hover:bg-gray-800 transition shadow-md"
        >
          <FileText className="w-5 h-5" /> Relatórios
        </button>
      </div>

      {/* Card de informações */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-5xl mx-auto bg-white dark:bg-zinc-800 rounded-2xl shadow-xl p-6 space-y-6"
      >
        <div className="flex items-center justify-center gap-3">
          <User className="w-8 h-8 text-blue-600 dark:text-blue-400" />
          <h2 className="text-3xl font-bold text-gray-800 dark:text-white">
            Dados do Utente
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {Object.entries(utente).map(([key, value]) => {
            if (key === "_id") value = value.$oid || value;
            if (key === "therapist") {
              key = "Idade";
              value = calcularIdade(utente.date_of_birth);
            }
            return (
              <div
                key={key}
                className="p-4 rounded-xl bg-gray-100 dark:bg-zinc-700/40 shadow-sm flex flex-col"
              >
                <span className="text-xs font-semibold uppercase text-gray-500 dark:text-gray-400">
                  {labels[key] || key}
                </span>
                <span className="text-sm text-gray-800 dark:text-gray-100 mt-1 break-words">
                  {typeof value === "object" ? JSON.stringify(value) : value || "—"}
                </span>
              </div>
            );
          })}
        </div>

        {/* Ações */}
        <div className="flex justify-center gap-4 pt-4 border-t dark:border-zinc-700">
          <button
            onClick={handleEdit}
            className="flex items-center gap-2 bg-yellow-500 hover:bg-yellow-600 text-white px-6 py-2 rounded transition shadow-md"
          >
            <Pencil className="w-4 h-4" /> Editar
          </button>
          <button
            onClick={handleDelete}
            className="flex items-center gap-2 bg-red-500 hover:bg-red-600 text-white px-6 py-2 rounded transition shadow-md"
          >
            <Trash2 className="w-4 h-4" /> Eliminar
          </button>
        </div>
      </motion.div>

      {/* Botão flutuante */}
      <button
        onClick={() => setMostrarFormulario(true)}
        className="fixed bottom-6 right-6 bg-blue-600 hover:bg-blue-700 text-white p-1 rounded shadow-xl transition-transform hover:scale-105"      
      >
        <Plus className="w-6 h-6" /> Novo Relatório 
      </button>

      {/* Modal */}
      <AnimatePresence>
        {mostrarFormulario && (
          <motion.div
            className="fixed inset-0 flex items-center justify-center bg-black/60 z-50 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="w-full max-w-2xl bg-white dark:bg-zinc-800 rounded-2xl shadow-xl p-6 overflow-y-auto max-h-[90vh]"
            >
              <h2 className="text-2xl font-bold text-center mb-6 dark:text-white">
                Novo Relatório
              </h2>

              <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                <input
                  type="text"
                  placeholder="Título do relatório"
                  {...register("title", { required: true })}
                  className="w-full border rounded-lg p-2 mb-4 dark:bg-zinc-700 dark:text-white"
                />

                <Controller
                  name="type_of_analysis"
                  control={control}
                  rules={{ required: true }}
                  render={({ field }) => (
                    <MultiSelect
                      {...field}
                      value={tiposSelecionados}
                      onChange={(e) => {
                        const selected = e.value || [];
                        setTiposSelecionados(selected);
                        field.onChange(selected);
                      }}
                      options={[
                        { label: "Articulação", value: "articulacao" },
                        { label: "Fonação", value: "fonacao" },
                        { label: "Prosódia", value: "prosodia" },
                        // { label: "Glota", value: "glota" },
                        // { label: "Reaprendizagem", value: "reaprendizagem" },
                      ]}
                      placeholder="Selecione os tipos de análise"
                      filter
                      display="chip"
                      className="w-full"
                    />
                  )}
                />

                {tiposSelecionados.map((tipo) => (
                  <textarea
                    key={tipo}
                    rows={3}
                    placeholder={`Comentário sobre ${tipo}`}
                    value={comentariosAnalises[tipo] || ""}
                    onChange={(e) =>
                      setComentariosAnalises((prev) => ({
                        ...prev,
                        [tipo]: e.target.value,
                      }))
                    }
                    className="w-full border rounded-lg p-2 mb-2 dark:bg-zinc-700 dark:text-white"
                  />
                ))}

                <input
                  type="date"
                  {...register("analysis_date", { required: true })}
                  className="w-full border rounded-lg p-2 mb-4 dark:bg-zinc-700 dark:text-white"
                />

                <textarea
                  rows={4}
                  placeholder="Observações principais"
                  {...register("observations")}
                  className="w-full border rounded-lg p-2 mb-4 dark:bg-zinc-700 dark:text-white"
                />

                <textarea
                  rows={3}
                  placeholder="Recomendações ao paciente"
                  {...register("recommendations")}
                  className="w-full border rounded-lg p-2 mb-4 dark:bg-zinc-700 dark:text-white"
                />

                <textarea
                  rows={2}
                  placeholder="Nota interna (visível apenas ao terapeuta)"
                  {...register("internal_note")}
                  className="w-full border rounded-lg p-2 mb-4 dark:bg-zinc-700 dark:text-white"
                />

                <select
                  {...register("status", { required: true })}
                  className="w-full border rounded-lg p-2 mb-4 dark:bg-zinc-700 dark:text-white"
                >
                  <option value="rascunho">Rascunho</option>
                  <option value="finalizado">Finalizado</option>
                </select>

                <div className="flex justify-between pt-4">
                  <button
                    type="submit"
                    className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded"
                  >
                    Submeter
                  </button>

                  <button
                    type="button"
                    onClick={() => setMostrarFormulario(false)}
                    className="bg-gray-400 hover:bg-gray-500 text-white px-4 py-2 rounded"
                  >
                    Cancelar
                  </button>
                  
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
