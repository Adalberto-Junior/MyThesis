
import React, { useEffect, useState } from "react";
import api from "../../../api";
import { useNavigate, useParams } from "react-router-dom";

import { Card, CardHeader, CardTitle, CardContent } from "../../../components/ui/card";
import { Button } from "../../../components/ui/button";

import { Loader2, Edit, Trash2, ListChecks, FileText, ArrowLeft } from "lucide-react";

// 🔹 Traduções de Processamentos
const processingLabels = {
  articulation: "Articulação",
  phonation: "Fonação",
  glotta: "Glota",
  prosody: "Prosódia",
  replearning: "Reaprendizagem",
};

// 🔹 Traduções de Campos de Steps
const stepLabels = {
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

const translateStepKey = (key) => stepLabels[key] || key.replace(/_/g, " ");

const formatValue = (key, value) => {
  if (key === "typeOfProcessing") {
    if (Array.isArray(value)) return value.map((v) => processingLabels[v] || v).join(", ");
    return processingLabels[value] || value;
  }
  if (typeof value === "object" && value !== null) return JSON.stringify(value, null, 2);
  if (key === "Id do Exercício" || key === "_id") return value?.$oid || value?.toString();
  return value?.toString() || "N/A";
};

export default function GenericExerciseDetail() {
  const [exercise, setExercise] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const { id } = useParams();

  useEffect(() => {
    const fetchExercise = async () => {
      try {
        const response = await api.get(`/utente/exercicio/${id}/`);
        setExercise(response.data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };
    fetchExercise();
  }, [id]);

  const handleEdit = () => {
    navigate(`/exercicios/genericos/detail/editar/${id}`);
  };

  const handleDelete = async () => {
    if (!window.confirm("Tem a certeza que deseja eliminar este exercício?")) return;
    try {
      await api.delete(`/utente/exercicio/${id}/`);
      navigate(-1);
    } catch (err) {
      console.error("Erro ao deletar:", err);
      alert("Erro ao eliminar exercício.");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 dark:bg-zinc-900">
        <Loader2 className="h-10 w-10 animate-spin text-primary mb-4" />
        <p className="text-lg font-semibold dark:text-white">
          Carregando exercício...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-red-100 dark:bg-red-900">
        <p className="text-lg font-semibold text-red-600 dark:text-red-300">
          Erro: {error.message}
        </p>
      </div>
    );
  }

  if (!exercise) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-zinc-900">
        <p className="text-lg dark:text-gray-300">
          Nenhum exercício encontrado.
        </p>
      </div>
    );
  }

  return (
    <div className="min-h-screen max-h-screen overflow-y-auto bg-gray-100 dark:bg-zinc-900">
      <div className="max-w-4xl mx-auto p-6 space-y-6 pb-32">
        {/* Botão de Voltar */}
        <div className="flex justify-start p-1.5">
          {/* <Button
            onClick={() => navigate(-1)}
            variant="outline"
            className="flex items-center gap-2 rounded"
          >
            <ArrowLeft size={16} /> Voltar
          </Button> */}
        </div>

        {/* Card Principal */}
        <Card>
          <CardHeader>
            <CardTitle className="text-3xl font-bold flex items-center gap-2">
              <FileText className="text-primary w-7 h-7" />
              Detalhes do Exercício
            </CardTitle>
          </CardHeader>

          <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(exercise).map(([key, value]) => {
              if (["user", "therapist", "steps", "userName", "_id"].includes(key)) return null;

              const labelMap = {
                name: "Nome do Exercício",
                description: "Descrição",
                type: "Tipo do Exercício",
                _id: "ID do Exercício",
                typeOfProcessing: "Tipo de Processamento",
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
                    {formatValue(key, value)}
                  </p>
                </div>
              );
            })}
          </CardContent>
        </Card>

        {/* Passos */}
        {Array.isArray(exercise.steps) && exercise.steps.length > 0 && (
          <Card>
            <CardHeader className="flex flex-row items-center gap-2">
              <ListChecks className="text-primary w-5 h-5" />
              <CardTitle className="text-xl">
                Passos ({exercise.steps.length})
              </CardTitle>
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
                    {Object.entries(step).map(([k, v]) =>
                      v !== "" ? (
                        <p key={k} className="text-sm text-gray-800 dark:text-gray-200">
                          <span className="font-medium">{translateStepKey(k)}:</span>{" "}
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

        {/* Botões de Ação */}
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
    </div>
  );
}
