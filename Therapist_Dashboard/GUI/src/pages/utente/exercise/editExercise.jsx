import React, { useEffect, useState } from "react";
import { useForm, useFieldArray, Controller } from "react-hook-form";
import { useParams, useNavigate } from "react-router-dom";
import api from "../../../api";
import { ErrorMessage } from "@hookform/error-message";
import { MultiSelect } from "primereact/multiselect";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "../../../components/ui/card";
import { Button } from "../../../components/ui/button";
import { PlusCircle, Trash2, Loader2 } from "lucide-react";

import "primereact/resources/themes/lara-light-blue/theme.css";
import "primereact/resources/primereact.min.css";
import "primeicons/primeicons.css";

export default function EditarExercicioForm() {
  const { id, id_ } = useParams();
  const [type, setType] = useState("");
  const [exercicio, setExercise] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);
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
      user: id,
      userName: "",
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

  const camposPorTipo = {
    palavras: ["Palavras", "Descrição", "ID"],
    frases: ["Frase", "Descrição", "ID"],
    leitura: ["Título", "Texto", "Descrição", "ID"],
    discurso: ["Questão", "Descrição", "ID"],
    diadococinesia: ["Tipo de Consoante", "Sílabas", "Descrição", "ID"],
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

  useEffect(() => {
    const fetchExercise = async () => {
      try {
        setLoading(true);
        setError(null);
        if (!id_) throw new Error("ID do exercício não fornecido");

        const response = await api.get(`/utente/exercicio/${id_}/`);
        const data = response.data;

        setExercise(data);
        reset({
          user: data.user || "",
          userName: data.userName || "",
          tipo: tipoPorLabel[data.type] ?? "novo",
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
        console.error("Erro ao buscar exercício:", err);
        setError("Erro ao buscar exercício.");
      } finally {
        setLoading(false);
      }
    };
    fetchExercise();
  }, [id_, reset]);

  const tipoSelecionado = watch("tipo");

  useEffect(() => {
    const subscription = watch((value) => {
      setType(value.tipo);
    });
    return () => subscription.unsubscribe();
  }, [watch]);

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
      setSaving(true);
      data.type = mapTipo(data.tipo);
      if (!Array.isArray(data.typeOfProcessing)) {
        data.typeOfProcessing = [data.typeOfProcessing];
      }
      await api.put(`/utente/exercicio/${id_}/`, data);
      alert("Exercício editado com sucesso!");
      navigate(-1);
    } catch (err) {
      console.error("Erro ao editar exercício:", err);
      alert("Erro ao editar exercício.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-zinc-900">
        <Loader2 className="animate-spin text-blue-500 w-8 h-8" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-zinc-900">
        <p className="text-lg font-semibold text-red-500">{error}</p>
      </div>
    );
  }

  if (!exercicio) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-zinc-900">
        <p className="text-lg font-semibold dark:text-white">
          Exercício não encontrado.
        </p>
      </div>
    );
  }

  const campos = camposPorTipo[tipoSelecionado] || [];
  const camposEn = camposPorTipoEn[tipoSelecionado] || [];

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-zinc-900 px-4 py-8">
      <Card className="w-full max-w-3xl shadow-xl dark:bg-zinc-800">
        <CardHeader>
          <CardTitle className="text-2xl text-center">Editar Exercício</CardTitle>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            {/* Hidden Fields */}
            <input type="hidden" {...register("user")} />
            <input type="hidden" {...register("therapist")} />
            <input type="hidden" {...register("userName")} />

            {/* Tipo */}
            <div>
              <label className="block text-sm font-medium mb-1">
                Tipo de Exercício <span className="text-red-500">*</span>
              </label>
              <select
                {...register("tipo", { required: "Campo obrigatório" })}
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 dark:bg-zinc-700 dark:border-zinc-600 dark:text-white"
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
                  <p className="text-red-500 text-xs mt-1">{message}</p>
                )}
              />
            </div>

            {/* Tipo Personalizado */}
            {tipoSelecionado === "novo" && (
              <div>
                <label className="block text-sm font-medium mb-1">
                  Tipo Personalizado <span className="text-red-500">*</span>
                </label>
                <input
                  {...register("type", { required: "Campo obrigatório" })}
                  className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 dark:bg-zinc-700 dark:border-zinc-600 dark:text-white"
                />
              </div>
            )}

            {/* Nome */}
            <div>
              <label className="block text-sm font-medium mb-1">
                Nome <span className="text-red-500">*</span>
              </label>
              <input
                {...register("name", { required: "Campo obrigatório" })}
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 dark:bg-zinc-700 dark:border-zinc-600 dark:text-white"
              />
            </div>

            {/* Descrição */}
            <div>
              <label className="block text-sm font-medium mb-1">Descrição</label>
              <input
                {...register("description")}
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 dark:bg-zinc-700 dark:border-zinc-600 dark:text-white"
              />
            </div>

            {/* Tipo de Processamento */}
            <div>
              <label className="block text-sm font-medium mb-1">
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
                      { label: "Glota", value: "glotta" },
                      { label: "Prosódia", value: "prosody" },
                      { label: "Reaprendizagem", value: "relearning" },
                      { label: "Fonológico", value: "phonological" },
                    ]}
                    placeholder="Selecione os tipos de processamento"
                    filter
                    display="chip"
                    className="w-full dark:bg-zinc-900 dark:border-zinc-600"
                  />
                )}
              />
              <ErrorMessage
                errors={errors}
                name="typeOfProcessing"
                render={({ message }) => (
                  <p className="text-red-500 text-xs mt-1">{message}</p>
                )}
              />
            </div>

            {/* Passos */}
            <div className="border rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-3">Passos</h3>
              {fields.map((field, index) => (
                <div key={field.id} className="mb-4 border p-3 rounded-md">
                  {(tipoSelecionado === "novo"
                    ? camposPorTipo["novo"]
                    : campos
                  ).map((campo, i) => {
                    const key =
                      tipoSelecionado === "novo"
                        ? campo.toLowerCase()
                        : camposEn[i];
                    const isTextarea = campo === "Texto";
                    return (
                      <div key={campo} className="mb-2">
                        <label className="block text-sm mb-1">
                          {campo} <span className="text-red-500">*</span>
                        </label>
                        {isTextarea ? (
                          <textarea
                            {...register(`steps.${index}.${key}`, {
                              required: true,
                            })}
                            className="w-full px-3 py-2 border rounded-md dark:bg-zinc-700 dark:border-zinc-600 dark:text-white"
                          />
                        ) : (
                          <input
                            {...register(`steps.${index}.${key}`, {
                              required: true,
                            })}
                            className="w-full px-3 py-2 border rounded-md dark:bg-zinc-700 dark:border-zinc-600 dark:text-white"
                          />
                        )}
                      </div>
                    );
                  })}
                  <Button
                    type="button"
                    onClick={() => remove(index)}
                    variant="destructive"
                    className="mt-2 flex items-center gap-2 rounded"
                  >
                    <Trash2 size={16} /> Remover passo
                  </Button>
                </div>
              ))}
              <Button
                type="button"
                onClick={appendStep}
                className="flex items-center gap-2 mt-2 rounded"
              >
                <PlusCircle size={18} /> Adicionar passo
              </Button>
            </div>

            <p className="text-xs text-gray-500 dark:text-gray-400">
              <span className="text-red-500">*</span> Campos obrigatórios
            </p>

            <CardFooter className="flex justify-between gap-3 pt-4">
              <Button type="submit" className=" w-30 flex items-center gap-2 rounded" disabled={saving}>
                {saving && <Loader2 className="animate-spin w-4 h-4" />}
                Guardar
              </Button>
              <Button
                type="button"
                onClick={() => navigate(-1)}
                variant="outline"
                className="w-30 flex items-center gap-2 rounded"
              >
                Cancelar
              </Button>
            </CardFooter>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}

