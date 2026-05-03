import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../../../api";

import { Card, CardHeader, CardTitle, CardContent } from "../../../components/ui/card";
import { Button } from "../../../components/ui/button";

import { Loader2, Edit, Trash2, ListChecks, FileText } from "lucide-react";

export default function ExerciseDetail() {
  const [exercise, setExercise] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const { id, id_ } = useParams();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get(`/utente/exercicio/${id_}/`);
        setExercise(response.data);
      } catch (error) {
        setError(error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id_]);

  const processingInPT = {
    articulation: "Articulação",
    phonation: "Fonação",
    glotta: "Glota",
    prosody: "Prosódia",
    replearning: "Reaprendizagem",
  };

  const stepInPT = {
    text: "Texto",
    title: "Título",
    description: "Instrução",
    word: "Palavra",
    sentence: "Frase",
    step: "Passo",
    question: "Pergunta",
    typeOfConsonant: "Tipo de Consoante",
    syllables: "Sílaba",
  };

  function translateKey(key) {
    return stepInPT[key] || key.replace(/_/g, " ");
  }

  const handleEdit = () => {
    navigate(`/utente/${id}/exercicio/editar/${id_}`);
  };

  const handleDelete = async () => {
    try {
      if (!window.confirm("Tem certeza que deseja eliminar este exercício?")) return;
      await api.delete(`/utente/exercicio/${id_}/`);
      navigate(-1);
    } catch (error) {
      console.error(`Erro ao deletar o exercício ${id_}:`, error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 dark:bg-zinc-900 px-4">
        <Loader2 className="h-10 w-10 animate-spin text-primary mb-4" />
        <p className="text-lg font-semibold dark:text-white">
          Carregando exercício...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-zinc-900 px-4">
        <p className="text-lg font-semibold text-red-600 dark:text-red-400">
          Erro ao carregar exercício: {error.message}
        </p>
      </div>
    );
  }

  if (!exercise) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-zinc-900 px-4">
        <p className="text-lg font-semibold dark:text-white">
          Exercício não encontrado.
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-3xl font-bold flex items-center gap-2">
            <FileText className="text-primary w-7 h-7" />
            Detalhes do Exercício
          </CardTitle>
        </CardHeader>

        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(exercise).map(([key, value]) => {
            if (key === "user" || key === "therapist" || key === "steps")
              return null;

            if (key === "typeOfProcessing") {
              value = Array.isArray(value)
                ? value.map((v) => processingInPT[v] || v).join(", ")
                : processingInPT[value] || value;
            }

            if (key === "_id") value = value?.$oid || value;
            if (typeof value === "object" && value !== null)
              value = JSON.stringify(value, null, 2);

            const labelMap = {
              name: "Nome do Exercício",
              description: "Descrição do Exercício",
              type: "Tipo do Exercício",
              userName: "Nome do Utente",
              typeOfProcessing: "Tipo de Processamento",
              _id: "ID do Exercício",
            };

            return (
              <div
                key={key}
                className="flex flex-col p-3 rounded-xl bg-gray-50 dark:bg-zinc-800 shadow-sm"
              >
                <span className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">
                  {labelMap[key] || key.replace(/_/g, " ")}
                </span>
                <p className="text-base font-semibold text-gray-900 dark:text-white">
                  {value || "N/A"}
                </p>
              </div>
            );
          })}
        </CardContent>
      </Card>

      {Array.isArray(exercise.steps) && exercise.steps.length > 0 && (
        <Card>
          <CardHeader className="flex flex-row items-center gap-2">
            <ListChecks className="text-primary w-5 h-5" />
            <CardTitle className="text-xl">Passos</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {exercise.steps.map((step, index) => (
              <div
                key={index}
                className="flex items-start gap-3 p-3 rounded-xl bg-gray-50 dark:bg-zinc-800 shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="flex items-center justify-center w-7 h-7 rounded-full bg-primary text-white text-sm font-bold shrink-0">
                  {index + 1}
                </div>
                <div className="space-y-1">
                  {Object.entries(step).map(([k, v], i) =>
                    v !== null && v !== "" ? (
                      <p key={i} className="text-sm text-gray-800 dark:text-gray-200">
                        <span className="font-medium">{translateKey(k)}:</span>{" "}
                        {typeof v === "string" ? v : JSON.stringify(v)}
                      </p>
                    ) : null
                  )}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      <div className="flex gap-4 justify-end">
        <Button
          onClick={handleEdit}
          variant="outline"
          className="flex items-center gap-2 rounded"
        >
          <Edit size={16} /> Editar
        </Button>
        <Button
          onClick={handleDelete}
          variant="destructive"
          className="flex items-center gap-2 rounded"
        >
          <Trash2 size={16} /> Eliminar
        </Button>
      </div>
    </div>
  );
}
