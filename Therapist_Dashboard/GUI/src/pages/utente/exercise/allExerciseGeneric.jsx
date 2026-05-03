import React, { useEffect, useState, useCallback } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useForm, useFieldArray, Controller } from "react-hook-form";
import { ErrorMessage } from "@hookform/error-message";
import api from "../../../api";
import { MultiSelect } from "primereact/multiselect";

import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "../../../components/ui/card";
import { Button } from "../../../components/ui/button";
import { Input } from "../../../components/ui/input";
import { Textarea } from "../../../components/ui/textarea";
import { Loader2, Plus, Trash2, ClipboardList } from "lucide-react";

export default function AllGenericExercise() {
  const [exercises, setExercises] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [type, setType] = useState("");

  const navigate = useNavigate();
  const { id } = useParams();

  const {
    register,
    handleSubmit,
    watch,
    control,
    reset,
    formState: { errors },
  } = useForm({
    defaultValues: { tipo: "", steps: [] },
  });

  const { fields, append, remove } = useFieldArray({ control, name: "steps" });
  const tipoSelecionado = watch("tipo");

  const camposPorTipo = {
    palavras: ["Palavras", "Instrução", "ID"],
    frases: ["Frase", "Instrução", "ID"],
    leitura: ["Título", "Texto", "Instrução", "ID"],
    discurso: ["Questão", "Instrução", "ID"],
    diadococinesia: ["Tipo de Consoante", "Sílabas", "Instrução", "ID"],
    novo: ["Instrução", "label", "valor", "ID"],
  };

  const camposPorTipoEn = {
    palavras: ["word", "description", "ID"],
    frases: ["sentence", "description", "ID"],
    leitura: ["title", "text", "description", "ID"],
    discurso: ["question", "description", "ID"],
    diadococinesia: ["typeOfConsonant", "syllables", "description", "ID"],
    novo: ["description", "label", "value", "ID"],
  };

  const mapTipo = useCallback((tipo) => {
      return {
        palavras: 'Repetição de Palavras',
        frases: 'Repetição de Frases',
        leitura: 'Atividades de Leitura',
        discurso: 'Discurso Espontâneo',
        diadococinesia: 'Diadococinésia'
      }[tipo] || tipo;
    }, []);

  const appendStep = () => {
    if (type === "novo") {
      append({ description: "", id: "", pairs: [{ label: "", value: "" }] });
    } else {
      const campos = camposPorTipo[type] || [];
      const novoStep = Object.fromEntries(campos.map((key) => [key, ""]));
      append(novoStep);
    }
  };

  const options = [
    { label: "Articulação", value: "articulation" },
    { label: "Fonação", value: "phonation" },
    { label: "Glota", value: "glotta" },
    { label: "Prosódia", value: "prosody" },
    { label: "Reaprendizagem", value: "replearning" },
    { label: "Fonológico", value: "phonological" },
  ];

  const onSubmit = async (data) => {
    try {
      if (typeof data.typeOfProcessing === "string") {
        data.typeOfProcessing = [data.typeOfProcessing];
      }
      data.type = mapTipo(data.type);
      await api.post(`/utente/exercicio/`, data);
      alert("Exercício adicionado com sucesso!");
      setMostrarFormulario(false);
      window.location.reload();
    } catch (error) {
      alert("Erro ao adicionar exercício.");
    }
  };

  useEffect(() => {
    if (tipoSelecionado) {
      setType(tipoSelecionado);
      reset({ ...watch(), type: tipoSelecionado, steps: [] });
      appendStep();
    }
  }, [tipoSelecionado]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get(`/utente/exercicio/`);
        setExercises(response.data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleOpen = (exerciseId) => {
    navigate(`detail/${exerciseId}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 dark:bg-zinc-900">
        <Loader2 className="animate-spin w-10 h-10 text-primary mb-3" />
        <p className="text-lg font-semibold dark:text-white">Carregando exercícios...</p>
      </div>
    );
  }

  return (
    <div className="min-h-189 mx-auto overflow-y-auto space-y-6">
      <div className="max-w-5xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-4xl font-bold dark:text-white flex items-center gap-2">
            <ClipboardList className="w-7 h-7 text-primary" />
            Lista dos Exercícios
          </h1>
          <Button onClick={() => setMostrarFormulario(true)} className="flex items-center gap-2 rounded">
            <Plus size={18} /> Novo Exercício
          </Button>
        </div>

        {error && (
          <Card className="p-4 mb-4 bg-red-100 border border-red-400 text-red-700">
            Erro: {error.message}
          </Card>
        )}

        {exercises.length === 0 ? (
          <Card className="p-6 text-center">
            <p className="text-gray-500 dark:text-gray-300">Nenhum exercício encontrado.</p>
          </Card>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {exercises.map((exercise) => (
              <Card
                key={exercise._id.$oid || exercise._id}
                className="hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => handleOpen(exercise._id.$oid || exercise._id)}
              >
                <CardHeader>
                  <CardTitle className="text-lg font-semibold">{exercise.name}</CardTitle>
                </CardHeader>
                <CardContent className="space-y-1 text-sm text-gray-700 dark:text-gray-300">
                  <p><strong>Tipo:</strong> {exercise.type}</p>
                  <p><strong>Descrição:</strong> {exercise.description || "NA"}</p>
                </CardContent>
                <CardFooter className="flex justify-end">
                  <Button size="sm" className="hover:bg-primary hover:text-white rounded">
                    Abrir
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        )}

        {mostrarFormulario && (
          <div className="fixed inset-0 z-40 bg-black bg-opacity-50 flex items-center justify-center">
            <div className="w-full max-w-2xl bg-white dark:bg-zinc-800 shadow-xl rounded-2xl p-6">
              <h2 className="text-2xl font-semibold text-center dark:text-white mb-4">
                Adicionar Exercício Genérico
              </h2>

              <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 max-h-[70vh] overflow-y-auto">
                {/* Tipo de Exercício */}
                <div>
                  <label className="block mb-1 text-sm font-medium">Tipo de Exercício *</label>
                  <select
                    {...register("tipo", { required: "Selecione um tipo." })}
                    className="w-full border rounded-md p-2 dark:bg-zinc-700 dark:border-zinc-600 dark:text-white"
                  >
                    <option value="">Selecione...</option>
                    <option value="palavras">Repetição de Palavras</option>
                    <option value="frases">Repetição de Frases</option>
                    <option value="leitura">Atividades de Leitura</option>
                    <option value="discurso">Discurso Espontâneo</option>
                    <option value="diadococinesia">Diadococinésia</option>
                    <option value="novo">Novo</option>
                  </select>
                  <ErrorMessage errors={errors} name="tipo" render={({ message }) => <p className="text-red-500 text-sm">{message}</p>} />
                </div>

                {/* Nome */}
                <div>
                  <label className="block mb-1 text-sm font-medium">Nome do Exercício *</label>
                  <Input {...register("name", { required: "Nome do exercício é obrigatório." })} />
                  <ErrorMessage errors={errors} name="name" render={({ message }) => <p className="text-red-500 text-sm">{message}</p>} />
                </div>

                {/* Descrição */}
                <div>
                  <label className="block mb-1 text-sm font-medium">Descrição</label>
                  <Input {...register("description")} />
                </div>

                {/* Tipo de Processamento */}
                <div>
                  <label className="block mb-1 text-sm font-medium">Tipo de Processamento *</label>
                  <Controller
                    name="typeOfProcessing"
                    control={control}
                    rules={{ required: "Selecione pelo menos um tipo." }}
                    render={({ field }) => (
                      <MultiSelect {...field} options={options} optionLabel="label" optionValue="value" filter placeholder="Selecione..." display="chip" className="w-full" />
                    )}
                  />
                  <ErrorMessage errors={errors} name="typeOfProcessing" render={({ message }) => <p className="text-red-500 text-sm">{message}</p>} />
                </div>

                {/* Passos */}
                <div>
                  <h3 className="text-lg font-semibold mb-2">Passos *</h3>
                  {fields.map((field, index) => (
                    <div key={field.id} className="mb-4 border p-3 rounded-md">
                      {(camposPorTipo[type] || []).map((campo, i) => {
                        const fieldName = camposPorTipoEn[type]?.[i];
                        return (
                          <div key={campo} className="mb-2">
                            <label className="block text-sm">{campo}</label>
                            {campo === "Texto" ? (
                              <Textarea {...register(`steps.${index}.${fieldName}`, { required: true })} />
                            ) : (
                              <Input {...register(`steps.${index}.${fieldName}`, { required: true })} />
                            )}
                          </div>
                        );
                      })}
                      <Button className="bg-red-600 hover:bg-red-700 rounded" type="button" variant="destructive" size="sm" onClick={() => remove(index)}>
                        <Trash2 size={16} className="mr-1" /> Remover
                      </Button>
                    </div>
                  ))}
                  <Button type="button" className="bg-green-600 hover:bg-green-700 rounded" variant="secondary" onClick={appendStep}>
                    <Plus size={16} className="mr-1" /> Adicionar passo
                  </Button>
                </div>

                {/* Botões */}
                <div className="flex justify-between mt-4">
                  <Button type="submit" className="bg-green-600 hover:bg-green-700 rounded">Adicionar</Button>
                  <Button type="button" className="bg-gray-600 hover:bg-gray-700 rounded" variant="secondary" onClick={() => setMostrarFormulario(false)}>Cancelar</Button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
