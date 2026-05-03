
import { useEffect, useState } from "react";
import api from "../../../api.jsx";
import { useNavigate, useParams } from "react-router-dom";
import html2pdf from "html2pdf.js";
import { ArrowLeft, Pencil, Trash2, FileDown, ShieldCheck, X, Loader2 } from "lucide-react";


export default function ReportList() {
  const [relatorios, setRelatorios] = useState([]);
  const [relatoriosFiltrados, setRelatoriosFiltrados] = useState([]);
  const navigate = useNavigate();
  const { id } = useParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filtros
  const [dataInicio, setDataInicio] = useState("");
  const [dataFim, setDataFim] = useState("");
  const [tipoSelecionado, setTipoSelecionado] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get(`/utente/${id}/relatorio/`);
        setRelatorios(response.data);
        setRelatoriosFiltrados(response.data);
      } catch (error) {
        setError(error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  // 🔎 Aplicar filtros
  useEffect(() => {
    let filtrados = relatorios;

    if (dataInicio) {
      filtrados = filtrados.filter(
        (rel) => new Date(rel.analysis_date) >= new Date(dataInicio)
      );
    }

    if (dataFim) {
      filtrados = filtrados.filter(
        (rel) => new Date(rel.analysis_date) <= new Date(dataFim)
      );
    }

    if (tipoSelecionado) {
      filtrados = filtrados.filter((rel) =>
        rel.type_of_analysis?.includes(tipoSelecionado)
      );
    }

    setRelatoriosFiltrados(filtrados);
  }, [dataInicio, dataFim, tipoSelecionado, relatorios]);

  const resetFiltros = () => {
    setDataInicio("");
    setDataFim("");
    setTipoSelecionado("");
    setRelatoriosFiltrados(relatorios);
  };

  const onEdit = (rel) => {
    const id_ = rel._id.$oid || rel._id;
    navigate(`/utente/${id}/relatorio/edit/${id_}`);
  };

  // const onDelete = async (relId) => {
  //   if (window.confirm("Tem certeza que deseja eliminar este relatório?")) {
  //     try {
  //       const relId_ = relId.$oid || relId;
  //       await api.delete(`/utente/${relId_}/relatorio/`);
  //       setRelatorios(relatorios.filter((rel) => rel._id !== relId));
  //     } catch (error) {
  //       console.error("Erro ao eliminar relatório:", error);
  //       alert("Erro ao eliminar relatório. Por favor, tente novamente.");
  //     }
  //   }
  // };

  // const exportarPDF = async (rel, index, incluirNotaInterna) => {
  //   try {
  //     const element = document.getElementById(`relatorio-${index}`);
  //     if (!element) {
  //       console.error(`Elemento com id relatorio-${index} não encontrado.`);
  //       return;
  //     }

  //     const notaEl = element.querySelector(".nota-interna");
  //     const originalDisplay = notaEl?.style?.display;
  //     if (!incluirNotaInterna && notaEl) notaEl.style.display = "none";

  //     const opt = {
  //       margin: 0.5,
  //       filename: `${rel.title.replace(/\s+/g, "_")}_${rel.analysis_date}.pdf`,
  //       image: { type: "jpeg", quality: 0.98 },
  //       html2canvas: { scale: 2, logging: true }, // logging ajuda a debugar
  //       jsPDF: { unit: "in", format: "letter", orientation: "portrait" },
  //     };

  //     console.log("🔄 Gerando PDF para:", rel.title);
  //     await html2pdf().set(opt).from(element).save();
  //     console.log("✅ PDF gerado com sucesso!");
      
  //     if (notaEl) notaEl.style.display = originalDisplay || "";
  //   } catch (err) {
  //     console.error("❌ Erro ao gerar PDF:", err);
  //     alert("Ocorreu um erro ao exportar o relatório. Veja o console para detalhes.");
  //   }
  // };


  // NÃO FUNCIONA CORRETAMENTE - PROBLEMA POR RESOLVER
  const exportarPDF = async (rel, index, incluirNotaInterna) => {
    try {
      const element = document.getElementById(`relatorio-${index}`);
      if (!element) {
        console.error(`Elemento com id relatorio-${index} não encontrado.`);
        return;
      }

     
      const clone = element.cloneNode(true);
      clone.style.backgroundColor = "white";
      clone.style.color = "rgb(17, 24, 39)"; // text-gray-900

      // Converter todas as cores internas para RGB
      const allNodes = clone.querySelectorAll("*");
      allNodes.forEach((node) => {
        const style = window.getComputedStyle(node);

        // Força cor de fundo para RGB ou branco
        const bg = style.backgroundColor;
        if (bg && bg.startsWith("oklch")) node.style.backgroundColor = "white";
        else if (bg && bg !== "rgba(0, 0, 0, 0)") node.style.backgroundColor = bg;

        // Força cor do texto para RGB
        const color = style.color;
        if (color && color.startsWith("oklch")) node.style.color = "rgb(17, 24, 39)";
        else if (color) node.style.color = color;
      });


      if (!incluirNotaInterna) {
        const notaEl = clone.querySelector(".nota-interna");
        if (notaEl) notaEl.style.display = "none";
      }

      // Configuração do PDF
      const opt = {
        margin: 0.5,
        filename: `${rel.title.replace(/\s+/g, "_")}_${rel.analysis_date}.pdf`,
        image: { type: "jpeg", quality: 0.98 },
        html2canvas: { scale: 2 },
        jsPDF: { unit: "in", format: "letter", orientation: "portrait" },
      };

      console.log("🔄 Gerando PDF para:", rel.title);
      await html2pdf().set(opt).from(clone).save();
      console.log("✅ PDF gerado com sucesso!");
    } catch (err) {
      console.error("❌ Erro ao gerar PDF:", err);
      alert("Ocorreu um erro ao exportar o relatório. Veja o console para detalhes.");
    }
  };



  const tipoDeAnalise = {
    articulacao: "Articulação",
    fonacao: "Fonação",
    prosodia: "Prosódia",
    glota: "Glota",
    reaprendizagem: "Reaprendizagem",
  };

  if (loading) {
      return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 dark:bg-zinc-900">
          <Loader2 className="animate-spin w-10 h-10 text-primary mb-3" />
          <p className="text-lg font-semibold dark:text-white">Carregando os dados...</p>
        </div>
      );
    }

  if (error)
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-zinc-900">
        <p className="text-xl text-red-500">Erro: {error.message}</p>
      </div>
    );

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-zinc-900 px-4 py-8">
      {/* Botão voltar */}
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 mb-8 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded shadow-md transition"
      >
        <ArrowLeft className="w-5 h-5" /> Voltar
      </button>

      {/* Cabeçalho */}
      <div className="text-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800 dark:text-white">
          Relatórios
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Histórico completo das análises e observações clínicas
        </p>
      </div>

      {/* Filtros */}
      <div className="max-w-5xl mx-auto bg-white dark:bg-zinc-800 rounded-xl shadow p-4 mb-8 border border-gray-200 dark:border-zinc-700">
        <h2 className="text-lg font-semibold mb-3 text-gray-700 dark:text-gray-200">
          Filtrar Relatórios
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm text-gray-600 dark:text-gray-300 mb-1">
              Data Início
            </label>
            <input
              type="date"
              value={dataInicio}
              onChange={(e) => setDataInicio(e.target.value)}
              className="w-full p-2 rounded border dark:bg-zinc-700 dark:border-zinc-600 dark:text-white"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-600 dark:text-gray-300 mb-1">
              Data Fim
            </label>
            <input
              type="date"
              value={dataFim}
              onChange={(e) => setDataFim(e.target.value)}
              className="w-full p-2 rounded border dark:bg-zinc-700 dark:border-zinc-600 dark:text-white"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-600 dark:text-gray-300 mb-1">
              Tipo de Análise
            </label>
            <select
              value={tipoSelecionado}
              onChange={(e) => setTipoSelecionado(e.target.value)}
              className="w-full p-2 rounded border dark:bg-zinc-700 dark:border-zinc-600 dark:text-white"
            >
              <option value="">Todos</option>
              {Object.entries(tipoDeAnalise).map(([key, label]) => (
                <option key={key} value={key}>
                  {label}
                </option>
              ))}
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={resetFiltros}
              className="flex items-center gap-2 px-4 py-2 bg-gray-200 hover:bg-gray-300 dark:bg-zinc-600 dark:hover:bg-zinc-500 rounded w-full justify-center"
            >
              <X className="w-4 h-4" /> Limpar Filtros
            </button>
          </div>
        </div>
      </div>

      {/* Lista de relatórios */}
      <div className="max-w-5xl mx-auto space-y-10">
        {relatoriosFiltrados.length === 0 ? (
          <p className="text-center text-xl text-gray-500 dark:text-gray-300 py-20">
            Nenhum relatório encontrado para os filtros aplicados.
          </p>
        ) : (
          relatoriosFiltrados.map((rel, index) => (
            <div
              key={rel._id}
              id={`relatorio-${index}`}
              className="bg-white dark:bg-zinc-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-zinc-700"
            >
              {/* Cabeçalho do relatório */}
              <div className="flex justify-between items-center border-b border-gray-300 dark:border-zinc-700 pb-4 mb-4">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                  <ShieldCheck className="w-5 h-5 text-blue-600" /> {rel.title}
                </h2>
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  {new Date(rel.analysis_date).toLocaleDateString()}
                </span>
              </div>

              {/* Conteúdo */}
              <div className="space-y-3 text-gray-700 dark:text-gray-300">
                <div>
                  <strong>Tipo de Análise:</strong>{" "}
                  {rel.type_of_analysis?.map((tipo, idx) => (
                    <span
                      key={idx}
                      className="inline-block bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 px-2 py-1 rounded-full text-xs mr-2"
                    >
                      {tipoDeAnalise[tipo] || tipo}
                    </span>
                  ))}
                </div>
                {rel.observations && (
                  <p>
                    <strong>Observações Clínicas:</strong> {rel.observations}
                  </p>
                )}
                {rel.analysis?.length > 0 && (
                  <div>
                    <strong>Comentários da Análise:</strong>
                    <ul className="list-disc list-inside mt-1 space-y-1">
                      {rel.analysis.map((c, i) => (
                        <li key={i}>
                          <span className="font-semibold">
                            {tipoDeAnalise[c.tipo] || c.tipo}:
                          </span>{" "}
                          {c.resultado}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {rel.recommendations && (
                  <p>
                    <strong>Recomendações:</strong> {rel.recommendations}
                  </p>
                )}
                {rel.internal_note && (
                  <p className="nota-interna text-xs italic text-red-500 dark:text-red-400">
                    <strong>Nota Interna:</strong> {rel.internal_note}
                  </p>
                )}
                <div className="grid grid-cols-2 gap-2 text-sm text-gray-600 dark:text-gray-400 pt-2">
                  <p>
                    <strong>Status:</strong> {rel.status}
                  </p>
                  <p>
                    <strong>Visualizações:</strong> {rel.views || 0}  
                  </p>
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  <strong>Criado em:</strong>{" "}
                  {new Date(rel.created_at).toLocaleDateString()}
                </div>
                
              </div>

              {/* Ações */}
              <div className="flex justify-between items-center mt-6 flex-wrap gap-3">
                <div className="flex gap-3">
                  <button
                    onClick={() => onEdit(rel)}
                    className="flex items-center gap-2 px-4 py-2 bg-yellow-500 hover:bg-yellow-600 text-white rounded shadow-sm transition"
                  >
                    <Pencil className="w-4 h-4" /> Editar
                  </button>
                  <button
                    onClick={() => onDelete(rel._id)}
                    className="flex items-center gap-2 px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded shadow-sm transition"
                  >
                    <Trash2 className="w-4 h-4" /> Eliminar
                  </button>
                </div>

                <div className="relative group">
                  <button className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded shadow-sm">
                    <FileDown className="w-4 h-4" /> Exportar
                  </button>
                  <div className="absolute hidden group-hover:block bg-white dark:bg-zinc-700 rounded shadow-md border border-gray-200 dark:border-zinc-600 mt-1 right-0 w-52 z-10">
                    <button
                      onClick={() => exportarPDF(rel, index, true)}
                      className="block w-full px-4 py-2 text-left rounded hover:bg-gray-100 dark:hover:bg-zinc-600 text-sm"
                    >
                      📄 Uso interno (com nota)
                    </button>
                    <button
                      onClick={() => exportarPDF(rel, index, false)}
                      className="block w-full px-4 py-2 text-left rounded hover:bg-gray-100 dark:hover:bg-zinc-600 text-sm"
                    >
                      👤 Para utente (sem nota)
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
