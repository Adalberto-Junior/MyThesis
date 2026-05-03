import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../../../api";
import ExerciseForm from "./exerciseForm2";

export default function ExerciseEdit() {
  const { id, exerciseId } = useParams();
  const [exercise, setExercise] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchExercise() {
      try {
        const res = await api.get(`/utente/rehabilitation/exercises/${exerciseId}`);
        setExercise(res.data);
        console.log("Fetched Exercise:", res.data);
      } catch (err) {
        console.error("Erro ao buscar exercício para edição:", err);
      }
    }
    fetchExercise();
  }, [id, exerciseId]);

  const handleUpdate = async (formData) => {
    try {
      await api.put(`/utente/rehabilitation/${id}/exercises/${exerciseId}`, formData);
      navigate(`/utente/${id}/exercises/${exerciseId}`);
    } catch (err) {
      console.error("Erro ao atualizar exercício:", err);
    }
  };

  const handleCancel = () => {
    // navigate(`/utente/${id}/exercises/${exerciseId}`);
    navigate(-1)
  };

  if (!exercise) return <p>Carregando...</p>;
  console.log("Exercise Data:", exercise);
  return (
    <ExerciseForm
      defaultValues={exercise}
      onSubmit={handleUpdate}
      onCancel={handleCancel}
      isEdit
    />
  );
}
