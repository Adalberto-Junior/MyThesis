import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../../../api";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "../../../components/ui/card";
import { Button } from "../../../components/ui/button";
import { Loader2, Plus, Target, NotebookPen, ClipboardList } from "lucide-react";

export default function ExercisesList() {
  const { id } = useParams(); // id do utente
  const [exercises, setExercises] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchExercises() {
      try {
        const response = await api.get(`/utente/rehabilitation/${id}/exercises/`);
        setExercises(response.data);
      } catch (err) {
        setError(err);
        console.error("Erro ao buscar Exercícios:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchExercises();
  }, [id]);

  const handleOpen = (exerciseId) => {
    navigate(`/utente/${id}/reabilitacao/exercicio/${exerciseId}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 dark:bg-zinc-900 px-4">
        <Loader2 className="h-10 w-10 animate-spin text-primary mb-4" />
        <p className="text-lg font-semibold dark:text-white">Carregando exercícios...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-zinc-900 px-4 py-8">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold dark:text-white flex items-center gap-2">
            <ClipboardList className="w-7 h-7 text-primary" />
            Lista de Exercícios de Reabilitação
          </h1>
          <Button
            onClick={() => navigate(`/utente/${id}/reabilitacao/novo-exercicio`)}
            className="flex items-center gap-2 rounded"
          >
            <Plus size={18} /> Novo Exercício
          </Button>
        </div>

        {error && (
          <p className="text-red-500 dark:text-red-400 mb-4">
            Erro ao carregar exercícios: {error.message}
          </p>
        )}

        {exercises.length === 0 ? (
          <Card className="p-6 text-center">
            <p className="text-gray-500 dark:text-gray-300">
              Nenhum exercício encontrado. Clique em <strong>“Novo Exercício”</strong> para adicionar.
            </p>
          </Card>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {exercises.map((ex) => (
              <Card
                key={ex._id}
                className="hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => handleOpen(ex._id)}
              >
                <CardHeader>
                  <CardTitle className="text-xl font-bold flex items-center gap-2">
                    <NotebookPen className="text-primary w-5 h-5" />
                    {ex.title}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
                    <Target className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                    <span className="font-semibold">Objetivo:</span>
                    <span>{ex.objective}</span>
                  </div>
                </CardContent>
                <CardFooter className="flex justify-end">
                  <Button size="sm"  className="hover:bg-primary hover:text-white rounded">
                    Abrir
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

