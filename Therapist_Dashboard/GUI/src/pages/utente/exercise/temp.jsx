import { useEffect, useState } from "react";
import { useForm, useFieldArray } from "react-hook-form";
import { useParams } from "react-router-dom";
import api from "../../services/api";

export default function AdicionarExercicioForm() {
  const { id } = useParams();
  const [tipoSelecionado, setTipoSelecionado] = useState("");
  const [exerciciosDisponiveis, setExerciciosDisponiveis] = useState([]);
  const [exercicioSelecionadoId, setExercicioSelecionadoId] = useState("");
  const [dadosExercicioSelecionado, setDadosExercicioSelecionado] = useState(null);
  const [modoEdicao, setModoEdicao] = useState("default");

  const {
    register,
    control,
    handleSubmit,
    setValue,
    reset,
    formState: { errors },
  } = useForm({
    defaultValues: {
      name: "",
      tipo: "",
      descricao: "",
      passos: [{ titulo: "", descricao: "" }],
    },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: "passos",
  });

  useEffect(() => {
    if (tipoSelecionado) {
      api.get(`/exercicios?tipo=${tipoSelecionado}`).then((res) => {
        setExerciciosDisponiveis(res.data);
      });
    } else {
      setExerciciosDisponiveis([]);
      setExercicioSelecionadoId("");
      setDadosExercicioSelecionado(null);
    }
  }, [tipoSelecionado]);

  useEffect(() => {
    if (exercicioSelecionadoId) {
      api.get(`/exercicios/${exercicioSelecionadoId}`).then((res) => {
        setDadosExercicioSelecionado(res.data);
        reset(res.data);
      });
    }
  }, [exercicioSelecionadoId, reset]);

  const onSubmit = async (data) => {
    try {
      if (modoEdicao === "default") {
        await api.post(`/utente/${id}/exercicio`, { exerciseId: exercicioSelecionadoId });
      } else {
        await api.post(`/utente/${id}/exercicio`, data);
      }

      alert("Exercício adicionado com sucesso!");
      window.location.reload();
    } catch (error) {
      console.error("Erro ao adicionar exercício:", error);
      alert("Erro ao adicionar exercício. Tente novamente.");
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="block mb-1 text-sm font-medium text-gray-700 dark:text-black">Tipo de Exercício</label>
        <select
          {...register("tipo", { required: true })}
          value={tipoSelecionado}
          onChange={(e) => setTipoSelecionado(e.target.value)}
          className="w-full p-2 border rounded-md dark:bg-zinc-700 dark:text-white"
        >
          <option value="">Selecione um tipo</option>
          <option value="palavras">Palavras</option>
          <option value="frases">Frases</option>
          <option value="leitura">Leitura</option>
        </select>
        {errors.tipo && <span className="text-red-500 text-sm">Este campo é obrigatório</span>}
      </div>

      {exerciciosDisponiveis.length > 0 && (
        <div>
          <label className="block mb-1 text-sm font-medium text-gray-700 dark:text-black">Selecionar Exercício Existente</label>
          <select
            value={exercicioSelecionadoId}
            onChange={(e) => setExercicioSelecionadoId(e.target.value)}
            className="w-full p-2 border rounded-md dark:bg-zinc-700 dark:text-white"
          >
            <option value="">-- Escolha um exercício --</option>
            {exerciciosDisponiveis.map((ex) => (
              <option key={ex.id} value={ex.id}>{ex.name}</option>
            ))}
          </select>
        </div>
      )}

      {dadosExercicioSelecionado && (
        <div>
          <label className="block mb-1 text-sm font-medium text-gray-700 dark:text-black">Modo de Uso</label>
          <select
            value={modoEdicao}
            onChange={(e) => setModoEdicao(e.target.value)}
            className="w-full p-2 border rounded-md dark:bg-zinc-700 dark:text-white"
          >
            <option value="default">Usar exercício como está</option>
            <option value="personalizar">Personalizar exercício</option>
          </select>
        </div>
      )}

      {(modoEdicao === "personalizar" || !dadosExercicioSelecionado) && (
        <>
          <div>
            <label className="block mb-1 text-sm font-medium text-gray-700 dark:text-black">Nome do Exercício</label>
            <input
              {...register("name", { required: true })}
              className="w-full p-2 border rounded-md dark:bg-zinc-700 dark:text-white"
              type="text"
            />
            {errors.name && <span className="text-red-500 text-sm">Este campo é obrigatório</span>}
          </div>

          <div>
            <label className="block mb-1 text-sm font-medium text-gray-700 dark:text-black">Descrição</label>
            <textarea
              {...register("descricao", { required: true })}
              className="w-full p-2 border rounded-md dark:bg-zinc-700 dark:text-white"
            />
            {errors.descricao && <span className="text-red-500 text-sm">Este campo é obrigatório</span>}
          </div>

          <div>
            <label className="block mb-1 text-sm font-medium text-gray-700 dark:text-black">Passos</label>
            {fields.map((item, index) => (
              <div key={item.id} className="mb-2 p-2 border rounded-md">
                <input
                  {...register(`passos.${index}.titulo`, { required: true })}
                  className="w-full mb-1 p-1 border rounded-md dark:bg-zinc-700 dark:text-white"
                  placeholder="Título do passo"
                />
                <textarea
                  {...register(`passos.${index}.descricao`, { required: true })}
                  className="w-full p-1 border rounded-md dark:bg-zinc-700 dark:text-white"
                  placeholder="Descrição do passo"
                />
                <button type="button" onClick={() => remove(index)} className="text-red-500 text-sm mt-1">Remover</button>
              </div>
            ))}
            <button
              type="button"
              onClick={() => append({ titulo: "", descricao: "" })}
              className="mt-2 px-4 py-2 bg-blue-500 text-white rounded-md"
            >
              Adicionar Passo
            </button>
          </div>
        </>
      )}

      <button type="submit" className="w-full py-2 px-4 bg-green-600 text-white rounded-md">Salvar</button>
    </form>
  );
}
