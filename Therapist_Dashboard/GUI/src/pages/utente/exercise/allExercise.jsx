import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useForm, useFieldArray, Controller } from "react-hook-form";
import { ErrorMessage } from "@hookform/error-message";
import api from "../../../api";
import FloatingForm from "./floatingExerciseForm";
import { MultiSelect } from "primereact/multiselect";

import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "../../../components/ui/card";
import { Button } from "../../../components/ui/button";
import { Input } from "../../../components/ui/input";
import { Textarea } from "../../../components/ui/textarea";
import { Loader2, Plus, Trash2, ClipboardList } from "lucide-react";

export default function AllExercise() {
  const [exercises, setExercises] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState(null);

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
  const [type, setType] = useState("");

  const camposPorTipo = {
    palavras: ["Palavras", "Instrução", "ID"],
    frases: ["Frase", "Instrução", "ID"],
    leitura: ["Título", "Texto", "Instrução", "ID"],
    discurso: ["Questão", "Instrução", "ID"],
    diadococinesia: ["Tipo de Consoante", "Sílabas", "Instrução", "ID"],
    novo: ["descrição", "label", "valor", "ID"],
  };

  const camposPorTipoEn = {
    palavras: ["word", "description", "ID"],
    frases: ["sentence", "description", "ID"],
    leitura: ["title", "text", "description", "ID"],
    discurso: ["question", "description", "ID"],
    diadococinesia: ["typeOfConsonant", "syllables", "description", "ID"],
    novo: ["description", "label", "value", "ID"],
  };

  const appendStep = () => {
    if (type === "novo") {
      append({
        description: "",
        id: "",
        pairs: [{ label: "", value: "" }],
      });
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

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get(`/utente/${id}/exercicio/`);
        setExercises(response.data);
      } catch (error) {
        setError(error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  useEffect(() => {
    if (tipoSelecionado) {
      setType(tipoSelecionado);
      reset({ ...watch(), type: tipoSelecionado, steps: [] });
      appendStep();
    }
  }, [tipoSelecionado]);

  const onSubmit = async (data) => {
    try {
      await api.post(`/utente/${id}/exercicio/`, data);
      alert("Exercício adicionado com sucesso!");
      setShowForm(false);
      window.location.reload();
    } catch (error) {
      alert("Erro ao adicionar exercício.");
    }
  };

  const handleOpen = (exerciseId) => {
    navigate(`/utente/${id}/exercicio/${exerciseId}`);
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
    <div className="min-h-screen bg-gray-100 dark:bg-zinc-900 px-4 py-8">
      <div className="max-w-5xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold dark:text-white flex items-center gap-2">
            <ClipboardList className="w-7 h-7 text-primary" />
            Lista de Exercícios
          </h1>
          <Button onClick={() => setShowForm(true)} className="flex items-center gap-2 rounded">
            <Plus size={18} /> Novo Exercício
          </Button>
        </div>

        {exercises.length === 0 ? (
          <Card className="p-6 text-center">
            <p className="text-gray-500 dark:text-gray-300">
              Nenhum exercício encontrado para este utente.
            </p>
          </Card>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {exercises.map((exercise) => (
              <Card 
                 key={exercise._id.$oid || exercise._id}
                 className="hover:shadow-lg transition-shadow cursor-pointer"
                 onClick={() => handleOpen(exercise._id.$oid || exercise._id)}>
                <CardHeader>
                  <CardTitle className="text-lg font-semibold">{exercise.name}</CardTitle>
                </CardHeader>
                <CardContent className="space-y-1 text-sm text-gray-700 dark:text-gray-300">
                  <p><strong>Tipo:</strong> {exercise.type}</p>
                  <p><strong>Descrição:</strong> {exercise.description}</p>
                </CardContent>
                <CardFooter className="flex justify-end ">
                  <Button size="sm"  className="hover:bg-primary hover:text-white rounded">
                    Abrir
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        )}

        {showForm && (
          <FloatingForm
            onClose={() => setShowForm(false)}
            onSubmit={handleSubmit(onSubmit)}
            control={control}
            register={register}
            errors={errors}
            fields={fields}
            appendStep={appendStep}
            remove={remove}
            options={options}
            type={type}
          />
        )}
      </div>
    </div>
  );
}
