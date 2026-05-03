import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../../../api";
import { Card, CardHeader, CardTitle, CardContent } from "../../../components/ui/card";
import { Button } from "../../../components/ui/button";
import { Loader2, Edit, Trash2, ImageIcon, Video, Volume2 } from "lucide-react";
import { Tag, Target, FileText, Clock, Repeat, Gauge, MessageSquare, StickyNote, User } from "lucide-react";
import { ListChecks } from "lucide-react";

export default function ExerciseDetails() {
  const { id, exerciseId } = useParams();
  const [exercise, setExercise] = useState(null);
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const BACKEND_URL = "http://localhost:5000";

  useEffect(() => {
    async function fetchExercise() {
      try {
        const res = await api.get(`/utente/rehabilitation/exercises/${exerciseId}`);
        setExercise(res.data);
      } catch (err) {
        setError(err);
        console.error("Erro ao buscar exercício:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchExercise();
  }, [id, exerciseId]);

  const handleDelete = async () => {
    if (confirm("Tem certeza que deseja eliminar este exercício?")) {
      try {
        await api.delete(`/utente/rehabilitation/exercises/${exerciseId}`);
        navigate(-1);
      } catch (err) {
        console.error("Erro ao eliminar exercício:", err);
      }
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 dark:bg-zinc-900 px-4">
        <Loader2 className="h-10 w-10 animate-spin text-primary mb-4" />
        <p className="text-lg font-semibold dark:text-white">Carregando exercício...</p>
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
          <CardTitle className="text-3xl font-bold">{exercise.title}</CardTitle>
        </CardHeader>
        

<CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
  <div className="flex items-start gap-3 p-3 rounded-xl bg-gray-50 dark:bg-zinc-800 shadow-sm">
    <Tag className="text-primary w-5 h-5 mt-1" />
    <div>
      <span className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">Categoria</span>
      <p className="text-base font-semibold text-gray-900 dark:text-white">{exercise.category}</p>
    </div>
  </div>

  <div className="flex items-start gap-3 p-3 rounded-xl bg-gray-50 dark:bg-zinc-800 shadow-sm">
    <Target className="text-primary w-5 h-5 mt-1" />
    <div>
      <span className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">Objetivo</span>
      <p className="text-base font-semibold">{exercise.objective}</p>
    </div>
  </div>

  <div className="flex items-start gap-3 p-3 rounded-xl bg-gray-50 dark:bg-zinc-800 shadow-sm md:col-span-2">
    <FileText className="text-primary w-5 h-5 mt-1" />
    <div>
      <span className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">Descrição</span>
      <p className="text-base">{exercise.description}</p>
    </div>
  </div>

  <div className="flex items-start gap-3 p-3 rounded-xl bg-gray-50 dark:bg-zinc-800 shadow-sm">
    <Clock className="text-primary w-5 h-5 mt-1" />
    <div>
      <span className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">Duração</span>
      <p className="text-base font-semibold">{exercise.duration} min</p>
    </div>
  </div>

  <div className="flex items-start gap-3 p-3 rounded-xl bg-gray-50 dark:bg-zinc-800 shadow-sm">
    <Repeat className="text-primary w-5 h-5 mt-1" />
    <div>
      <span className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">Repetições</span>
      <p className="text-base font-semibold">{exercise.repetitions}</p>
    </div>
  </div>

  <div className="flex items-start gap-3 p-3 rounded-xl bg-gray-50 dark:bg-zinc-800 shadow-sm">
    <Gauge className="text-primary w-5 h-5 mt-1" />
    <div>
      <span className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">Dificuldade</span>
      <p className="text-base font-semibold">{exercise.difficulty}</p>
    </div>
  </div>

  <div className="flex items-start gap-3 p-3 rounded-xl bg-gray-50 dark:bg-zinc-800 shadow-sm md:col-span-2">
    <MessageSquare className="text-primary w-5 h-5 mt-1" />
    <div>
      <span className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">Feedback</span>
      <p className="text-base">{exercise.feedback}</p>
    </div>
  </div>

  <div className="flex items-start gap-3 p-3 rounded-xl bg-gray-50 dark:bg-zinc-800 shadow-sm md:col-span-2">
    <StickyNote className="text-primary w-5 h-5 mt-1" />
    <div>
      <span className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">Notas do Terapeuta</span>
      <p className="text-base">{exercise.notes}</p>
    </div>
  </div>

  <div className="flex items-start gap-3 p-3 rounded-xl bg-gray-50 dark:bg-zinc-800 shadow-sm">
    <User className="text-primary w-5 h-5 mt-1" />
    <div>
      <span className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">Utente</span>
      <p className="text-base font-semibold">{exercise.userName}</p>
    </div>
  </div>
</CardContent>


      </Card>

      {(exercise.images?.length > 0 || exercise.videos?.length > 0 || exercise.audios?.length > 0) && (
        <Card>
          <CardHeader>
            <CardTitle className="text-xl">Mídia</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {exercise.images?.length > 0 && (
                <div>
                  <h3 className="flex items-center gap-2 font-semibold mb-2"><ImageIcon size={18}/> Imagens</h3>
                  <div className="space-y-2">
                    {exercise.images.map((imgUrl, idx) => (
                      <img
                        key={idx}
                        src={`${BACKEND_URL}${imgUrl}`}
                        alt={`Imagem ${idx + 1}`}
                        className="w-full rounded-xl shadow"
                      />
                    ))}
                  </div>
                </div>
              )}
              {exercise.videos?.length > 0 && (
                <div>
                  <h3 className="flex items-center gap-2 font-semibold mb-2"><Video size={18}/> Vídeos</h3>
                  <div className="space-y-2">
                    {exercise.videos.map((vidUrl, idx) => (
                      <video
                        key={idx}
                        src={`${BACKEND_URL}${vidUrl}`}
                        controls
                        className="w-full rounded-xl shadow"
                      />
                    ))}
                  </div>
                </div>
              )}
              {exercise.audios?.length > 0 && (
                <div>
                  <h3 className="flex items-center gap-2 font-semibold mb-2"><Volume2 size={18}/> Áudios</h3>
                  <div className="space-y-2">
                    {exercise.audios.map((audioUrl, idx) => (
                      <audio
                        key={idx}
                        src={`${BACKEND_URL}${audioUrl}`}
                        controls
                        className="w-full"
                      />
                    ))}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {exercise.steps?.length > 0 && (
        <Card>
          <CardHeader className="flex flex-row items-center gap-2">
            <ListChecks className="text-primary w-5 h-5" />
            <CardTitle className="text-xl">Passos</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {exercise.steps.map((step, idx) => (
              <div
                key={idx}
                className="flex items-start gap-3 p-3 rounded-xl bg-gray-50 dark:bg-zinc-800 shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="flex items-center justify-center w-7 h-7 rounded-full bg-primary text-white text-sm font-bold shrink-0">
                  {idx + 1}
                </div>
                <p className="text-base text-gray-800 dark:text-gray-200">
                  {step.instruction}
                </p>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      <div className="flex gap-4 justify-end">
        <Button
          onClick={() => navigate(`/utente/${id}/reabilitacao/exercicio/editar/${exerciseId}`)}
          variant="outline"
          className="flex items-center gap-2 rounded"
        >
          <Edit size={16}/> Editar
        </Button>
        <Button
          onClick={handleDelete}
          variant="destructive"
          className="flex items-center gap-2 rounded"
        >
          <Trash2 size={16}/> Eliminar
        </Button>
      </div>
    </div>
  );
}
