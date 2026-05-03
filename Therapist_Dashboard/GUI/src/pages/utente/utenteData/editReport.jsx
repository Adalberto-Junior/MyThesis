
import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../../../api";
import { MultiSelect } from "primereact/multiselect";
import { CheckCircle, XCircle, Loader2, ArrowLeft } from "lucide-react";

export default function EditReport() {
  const { id, id_ } = useParams();
  const navigate = useNavigate();

  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tiposSelecionados, setTiposSelecionados] = useState([]);
  const [comentariosAnalises, setComentariosAnalises] = useState({});

  useEffect(() => {
    async function fetchReport() {
      try {
        const res = await api.get(`/utente/relatorio/${id_}/`);
        const reportData = res.data;
        setReport(reportData);
        setTiposSelecionados(reportData.type_of_analysis || []);

        // Preenche os comentários
        const comentarios = {};
        reportData.analysis?.forEach(({ tipo, resultado }) => {
          comentarios[tipo] = resultado;
        });
        setComentariosAnalises(comentarios);
      } catch (err) {
        setError("Erro ao carregar o relatório.");
      } finally {
        setLoading(false);
      }
    }
    fetchReport();
  }, [id_]);

  const formatarTipo = (tipo) => {
    const mapa = {
      articulacao: "Articulação",
      fonacao: "Fonação",
      prosodia: "Prosódia",
      glota: "Glota",
      reaprendizagem: "Reaprendizagem",
    };
    return mapa[tipo] || tipo;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setReport((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const analises = tiposSelecionados.map((tipo) => ({
        tipo,
        resultado: comentariosAnalises[tipo] || "",
      }));

      const updatedReport = {
        ...report,
        analises,
        type_of_analysis: tiposSelecionados,
        views: report.views || 0,
      };

      await api.put(`/utente/relatorio/${id_}`, updatedReport);
      alert("✅ Relatório atualizado com sucesso!");
      navigate(`/utente/${id}/relatorio`);
    } catch (err) {
      console.error(err);
      alert("❌ Erro ao atualizar este relatório.");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-zinc-900">
        <Loader2 className="animate-spin w-8 h-8 text-blue-600" />
        <p className="mt-2 text-gray-700 dark:text-gray-300">Carregando...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-zinc-900">
        <XCircle className="w-10 h-10 text-red-500 mb-2" />
        <p className="text-lg text-red-600">{error}</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-zinc-900 p-6 flex flex-col items-center">
      <div className="w-full max-w-3xl bg-white dark:bg-zinc-800 shadow-lg rounded-xl p-6">
        {/* Cabeçalho */}
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-gray-800 dark:text-white">
            ✏️ Editar Relatório
          </h1>
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 px-3 py-1 text-sm bg-gray-200 hover:bg-gray-300 dark:bg-zinc-700 dark:hover:bg-zinc-600 rounded transition"
          >
            <ArrowLeft className="w-4 h-4" /> Voltar
          </button>
        </div>

        {/* Formulário */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Título */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Título do Relatório
            </label>
            <input
              type="text"
              name="title"
              value={report.title || ""}
              onChange={handleChange}
              className="mt-1 w-full p-2 border rounded-lg dark:bg-zinc-700 dark:text-white"
            />
          </div>

          {/* Data */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Data da Análise
            </label>
            <input
              type="date"
              name="analysis_date"
              value={report.analysis_date?.slice(0, 10) || ""}
              onChange={handleChange}
              className="mt-1 w-full p-2 border rounded-lg dark:bg-zinc-700 dark:text-white"
            />
          </div>

          {/* Tipo de Análise */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Tipo de Análise
            </label>
            <MultiSelect
              value={tiposSelecionados}
              options={[
                { label: "Articulação", value: "articulacao" },
                { label: "Fonação", value: "fonacao" },
                { label: "Prosódia", value: "prosodia" },
                // { label: "Glota", value: "glota" },
              ]}
              onChange={(e) => {
                const novosTipos = e.value || [];
                setTiposSelecionados(novosTipos);

                const novosComentarios = { ...comentariosAnalises };
                novosTipos.forEach((tipo) => {
                  if (!novosComentarios[tipo]) novosComentarios[tipo] = "";
                });
                setComentariosAnalises(novosComentarios);
              }}
              display="chip"
              className="w-full"
              placeholder="Selecione os tipos de análise"
            />
          </div>

          {/* Comentários de cada tipo */}
          {tiposSelecionados.map((tipo) => (
            <div key={tipo}>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Comentário sobre {formatarTipo(tipo)}
              </label>
              <textarea
                rows="3"
                className="mt-1 w-full border rounded-lg p-2 dark:bg-zinc-700 dark:text-white"
                value={comentariosAnalises[tipo] || ""}
                onChange={(e) =>
                  setComentariosAnalises({
                    ...comentariosAnalises,
                    [tipo]: e.target.value,
                  })
                }
              />
            </div>
          ))}

          {/* Observações */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Observações Clínicas
            </label>
            <textarea
              name="observations"
              rows="3"
              value={report.observations || ""}
              onChange={handleChange}
              className="mt-1 w-full p-2 border rounded-lg dark:bg-zinc-700 dark:text-white"
            />
          </div>

          {/* Recomendações */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Recomendações ao Paciente
            </label>
            <textarea
              name="recommendations"
              rows="3"
              value={report.recommendations || ""}
              onChange={handleChange}
              className="mt-1 w-full p-2 border rounded-lg dark:bg-zinc-700 dark:text-white"
            />
          </div>

          {/* Nota interna */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Nota Interna
            </label>
            <textarea
              name="internal_note"
              rows="3"
              value={report.internal_note || ""}
              onChange={handleChange}
              className="mt-1 w-full p-2 border rounded-lg dark:bg-zinc-700 dark:text-white"
            />
          </div>

          {/* Status */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Status do Relatório
            </label>
            <select
              name="status"
              value={report.status || ""}
              onChange={handleChange}
              className="mt-1 w-full p-2 border rounded-lg dark:bg-zinc-700 dark:text-white"
            >
              <option value="">Selecione...</option>
              <option value="rascunho">Rascunho</option>
              <option value="finalizado">Finalizado</option>
            </select>
          </div>

          {/* Visualizações */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Visualizações
            </label>
            <input
              type="number"
              name="views"
              min="0"
              value={report.views || 0}
              onChange={handleChange}
              className="mt-1 w-full p-2 border rounded-lg dark:bg-zinc-700 dark:text-white"
            />
          </div>

          {/* Botões */}
          <div className="flex justify-between items-center pt-4">
            <button
              type="submit"
              className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded shadow-md transition"
            >
              <CheckCircle className="w-4 h-4" /> Salvar Alterações
            </button>
            <button
              type="button"
              onClick={() => navigate(-1)}
              className="flex items-center gap-2 bg-gray-300 hover:bg-gray-400 text-gray-900 px-4 py-2 rounded shadow-md transition"
            >
              Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
