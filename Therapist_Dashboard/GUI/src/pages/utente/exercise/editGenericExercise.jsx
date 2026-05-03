import React, { useEffect, useState, useCallback } from "react";
import { useForm, useFieldArray, Controller } from "react-hook-form";
import { useParams, useNavigate } from "react-router-dom";
import api from "../../../api";
import { ErrorMessage } from "@hookform/error-message";
import { MultiSelect } from "primereact/multiselect";

import { Loader2, Plus, Trash2, Save, X } from "lucide-react";

import "primereact/resources/themes/lara-light-blue/theme.css";
import "primereact/resources/primereact.min.css";
import "primeicons/primeicons.css";

export default function EditarGenericExercicioForm() {
  const { id } = useParams();
  const [type, setType] = useState("");
  const [exercicio, setExercise] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    control,
    watch,
    reset,
    formState: { errors },
  } = useForm({
    defaultValues: {
      tipo: "",
      type: "",
      name: "",
      description: "",
      typeOfProcessing: "",
      steps: [],
      therapist: "",
      ID: "",
    },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: "steps",
  });

  const camposPorTipo = {
    palavras: ["Palavras", "Instrução", "ID"],
    frases: ["Frase", "Instrução", "ID"],
    leitura: ["Título", "Texto", "Instrução", "ID"],
    discurso: ["Questão", "Instrução", "ID"],
    diadococinesia: ["Tipo de Consoante", "Sílabas", "Instrução", "ID"],
    novo: ["label", "valor", "ID"],
  };

  const camposPorTipoEn = {
    palavras: ["word", "description", "ID"],
    frases: ["sentence", "description", "ID"],
    leitura: ["title", "text", "description", "ID"],
    discurso: ["question", "description", "ID"],
    diadococinesia: ["typeOfConsonant", "syllables", "description", "ID"],
    novo: ["label", "value", "ID"],
  };

  const tipoPorLabel = {
    "Repetição de Palavras": "palavras",
    "Repetição de Frases": "frases",
    "Atividades de Leitura": "leitura",
    "Discurso Espontâneo": "discurso",
    Diadococinésia: "diadococinesia",
  };

  const mapTipo = (tipo) =>
    ({
      palavras: "Repetição de Palavras",
      frases: "Repetição de Frases",
      leitura: "Atividades de Leitura",
      discurso: "Discurso Espontâneo",
      diadococinesia: "Diadococinésia",
    }[tipo] || tipo);

  useEffect(() => {
    const fetchExercise = async () => {
      try {
        setLoading(true);
        setError(null);
        if (!id) throw new Error("ID do exercício não fornecido");

        const response = await api.get(`/utente/exercicio/${id}/`);
        const data = response.data;
        setExercise(data);

        reset({
          tipo: tipoPorLabel[data.type] || "novo",
          type: data.type || "",
          name: data.name || "",
          description: data.description || "",
          typeOfProcessing: Array.isArray(data.typeOfProcessing)
            ? data.typeOfProcessing
            : [data.typeOfProcessing],
          steps: data.steps || [],
          therapist: data.therapist || "",
          ID: data.ID || "",
        });
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchExercise();
  }, [id, reset]);

  const tipoSelecionado = watch("tipo");

  const appendStep = () => {
    if (tipoSelecionado === "novo") {
      append({ label: "", value: "" });
    } else {
      const campos = camposPorTipo[tipoSelecionado] || [];
      const novoStep = Object.fromEntries(
        campos.map((_, i) => [camposPorTipoEn[tipoSelecionado][i], ""])
      );
      append(novoStep);
    }
  };

  const onSubmit = async (data) => {
    try {
      data.type = mapTipo(data.tipo);
      if (!Array.isArray(data.typeOfProcessing)) {
        data.typeOfProcessing = [data.typeOfProcessing];
      }
      if (data.user === "") delete data.user;

      await api.put(`/utente/exercicio/${id}/`, data);
      alert("Exercício editado com sucesso!");
      navigate(-1);
    } catch (err) {
      console.error("Erro ao editar exercício:", err);
      alert(`Erro ao editar exercício: ${err.response?.data?.error || ""}`);
    }
  };

  if (loading)
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 dark:bg-zinc-900">
        <Loader2 className="h-10 w-10 animate-spin text-primary mb-4" />
        <p className="text-lg font-semibold dark:text-white">
          Carregando exercício...
        </p>
      </div>
    );

  if (error)
    return (
      <div className="min-h-screen flex items-center justify-center bg-red-100 dark:bg-red-900">
        <p className="text-lg font-semibold text-red-600 dark:text-red-300">
          Erro: {error.message}
        </p>
      </div>
    );

  if (!exercicio)
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-zinc-900">
        <p className="text-lg dark:text-gray-300">
          Nenhum exercício encontrado.
        </p>
      </div>
    );

  const campos = camposPorTipo[tipoSelecionado] || [];
  const camposEn = camposPorTipoEn[tipoSelecionado] || [];

  return (
    <div className="min-h-screen flex justify-center items-start bg-gray-100 dark:bg-zinc-900 p-4 overflow-y-auto">
      <div className="w-full max-w-3xl m-10 bg-white dark:bg-zinc-800 shadow-lg rounded-2xl p-6 space-y-6">
        <h2 className="text-2xl font-bold text-center text-gray-900 dark:text-white">
          ✏️ Editar Exercício
        </h2>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Tipo */}
          <div>
            <label className="block text-sm font-medium mb-1 dark:text-gray-200">
              Tipo de Exercício <span className="text-red-500">*</span>
            </label>
            <select
              {...register("tipo", { required: "Campo obrigatório" })}
              className="w-full p-2 border rounded-lg dark:bg-zinc-700 dark:border-zinc-600 dark:text-white"
            >
              <option value="">Selecione...</option>
              <option value="palavras">Repetição de Palavras</option>
              <option value="frases">Repetição de Frases</option>
              <option value="leitura">Atividades de Leitura</option>
              <option value="discurso">Discurso Espontâneo</option>
              <option value="diadococinesia">Diadococinésia</option>
              <option value="novo">Novo</option>
            </select>
            <ErrorMessage
              errors={errors}
              name="tipo"
              render={({ message }) => (
                <p className="text-red-500 text-sm">{message}</p>
              )}
            />
          </div>

          {/* Tipo Customizado */}
          {tipoSelecionado === "novo" && (
            <div>
              <label className="block text-sm font-medium mb-1 dark:text-gray-200">
                Tipo Personalizado <span className="text-red-500">*</span>
              </label>
              <input
                {...register("type", { required: true })}
                className="w-full p-2 border rounded-lg dark:bg-zinc-700 dark:border-zinc-600 dark:text-white"
              />
            </div>
          )}

          {/* Nome */}
          <div>
            <label className="block text-sm font-medium mb-1 dark:text-gray-200">
              Nome <span className="text-red-500">*</span>
            </label>
            <input
              {...register("name", { required: true })}
              className="w-full p-2 border rounded-lg dark:bg-zinc-700 dark:border-zinc-600 dark:text-white"
            />
          </div>

          {/* Descrição */}
          <div>
            <label className="block text-sm font-medium mb-1 dark:text-gray-200">
              Descrição
            </label>
            <input
              {...register("description")}
              className="w-full p-2 border rounded-lg dark:bg-zinc-700 dark:border-zinc-600 dark:text-white"
            />
          </div>

          {/* Tipo de Processamento */}
          <div>
            <label className="block text-sm font-medium mb-1 dark:text-gray-200">
              Tipo de Processamento <span className="text-red-500">*</span>
            </label>
            <Controller
              name="typeOfProcessing"
              control={control}
              rules={{ required: "Campo obrigatório" }}
              render={({ field }) => (
                <MultiSelect
                  {...field}
                  options={[
                    { label: "Articulação", value: "articulation" },
                    { label: "Fonação", value: "phonation" },
                    // { label: "Glota", value: "glotta" },
                    { label: "Prosódia", value: "prosody" },
                    // { label: "Reaprendizagem", value: "relearning" },
                    // { label: "Fonológico", value: "phonological" },
                  ]}
                  placeholder="Selecione os tipos de processamento"
                  filter
                  display="chip"
                  className="w-full"
                />
              )}
            />
            <ErrorMessage
              errors={errors}
              name="typeOfProcessing"
              render={({ message }) => (
                <p className="text-red-500 text-sm">{message}</p>
              )}
            />
          </div>

          {/* Passos */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              Passos <span className="text-red-500">*</span>
            </h3>

            {fields.map((field, index) => (
              <div
                key={field.id}
                className="p-4 bg-gray-50 dark:bg-zinc-700 rounded-xl shadow-sm space-y-3"
              >
                {campos.map((campo, i) => {
                  const key =
                    tipoSelecionado === "novo"
                      ? campo.toLowerCase()
                      : camposEn[i];
                  const isTextarea = campo === "Texto";
                  return (
                    <div key={campo}>
                      <label className="block text-sm font-medium mb-1">
                        {campo}
                      </label>
                      {isTextarea ? (
                        <textarea
                          {...register(`steps.${index}.${key}`, {
                            required: true,
                          })}
                          lang="pt"
                          rows={6}
                          className="w-full p-2 border rounded-lg dark:bg-zinc-600 dark:text-white"
                        />
                      ) : (
                        <input
                          {...register(`steps.${index}.${key}`, {
                            required: true,
                          })}
                          className="w-full p-2 border rounded-lg dark:bg-zinc-600 dark:text-white"
                        />
                      )}
                    </div>
                  );
                })}
                <button
                  type="button"
                  onClick={() => remove(index)}
                  className="text-red-500 flex items-center rounded gap-1 hover:underline"
                >
                  <Trash2 size={16} /> Remover
                </button>
              </div>
            ))}

            <button
              type="button"
              onClick={appendStep}
              className="flex items-center gap-2 bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
            >
              <Plus size={16} /> Adicionar passo
            </button>
          </div>

          {/* Botões */}
          <div className="flex justify-between pt-4">
            <button
              type="submit"
              className="flex items-center gap-2 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
              <Save size={16} /> Guardar
            </button>
            <button
              type="button"
              onClick={() => navigate(-1)}
              className="flex items-center gap-2 bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
            >
              <X size={16} /> Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
