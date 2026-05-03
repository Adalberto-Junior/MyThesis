import { useEffect, useState, useMemo } from "react";
import { useParams } from "react-router-dom";
import api from "../../../../api";
import { Card, CardContent } from "../../../../components/ui/card";
import Accordion from "react-bootstrap/Accordion";
import { Button } from "../../../../components/ui/button";

import {
  groupF1F2DataToSpAcustic,
  mergeF1F2DataToCompare,
  mergeF1F2DataToCompareUnifiedGraph,
} from "../chartConfiguraction/groupChartData.jsx";
import { DisplayChart } from "../chartConfiguraction/ChartAccordion.jsx";

const BACKEND_URL = "http://localhost:5000";

export default function ArticulationResultPage() {
  const { id } = useParams();
  const [results, setResults] = useState([]);
  const [selectedDate, setSelectedDate] = useState("");
  const [selectedDates, setSelectedDates] = useState([]);
  const [compareMode, setCompareMode] = useState(false);
  const [unifiedGraphData, setUnifiedGraphData] = useState(null);
  const [unifiedMode, setUnifiedMode] = useState(false); // ✅ estado para saber se estamos no gráfico unificado
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  /** 🔎 Buscar resultados na API */
  useEffect(() => {
    async function fetchResults() {
      try {
        const res = await api.get(`/utente/${id}/analise/articulacao`);
        const data = Array.isArray(res.data) ? res.data : [];
        setResults(data);
        if (data.length > 0) {
          setSelectedDate(data[data.length - 1].date);
        }
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    }
    fetchResults();
  }, [id]);

  /** 🗓️ Datas únicas */
  const uniqueDates = useMemo(() => [...new Set(results.map((r) => r.date))], [results]);

  /** 🔢 Resultados filtrados */
  const filtered = useMemo(() => {
    return compareMode
      ? results.filter((res) => selectedDates.includes(res.date))
      : results.filter((res) => res.date === selectedDate);
  }, [results, compareMode, selectedDate, selectedDates]);

  /** 📊 Dados do gráfico */
  const chartData = useMemo(() => {
    return compareMode
      ? unifiedGraphData ?? mergeF1F2DataToCompare(filtered)
      : groupF1F2DataToSpAcustic(filtered);
  }, [compareMode, filtered, unifiedGraphData]);

  /** 🗑️ Eliminar resultados */
  const handleDelete = async () => {
    const type = filtered.find((item) => item.date === selectedDate)?.processing_type;
    if (!type) return;
    if (!window.confirm(`Tem certeza que deseja eliminar os resultados de ${selectedDate}?`)) return;

    try {
      await api.delete(`/utente/${id}/analise/${type}/${selectedDate}`);
      setResults((prev) => prev.filter((res) => res.date !== selectedDate));
      setSelectedDate("");
    } catch (err) {
      console.error("Erro ao deletar dados:", err);
      alert("Erro ao eliminar. Tente novamente.");
    }
  };

  /** 🎛️ Selector de datas */
  const renderDateSelector = () =>
    compareMode ? (
      <>
        <select
          multiple
          value={selectedDates}
          onChange={(e) =>
            setSelectedDates([...e.target.selectedOptions].map((o) => o.value))
          }
          className="mb-4 p-2 border rounded w-full h-48 overflow-auto
            bg-white text-black border-gray-300 dark:bg-zinc-800 dark:text-white dark:border-zinc-600"
        >
          {uniqueDates.map((date) => (
            <option key={date} value={date}>
              {date}
            </option>
          ))}
        </select>

        <h6 className="text-sm text-gray-600 dark:text-gray-400 mb-2">
          Usa Ctrl + clique para selecionar múltiplas datas.
        </h6>

        <div className="flex flex-wrap gap-2 mb-4">
          
          {uniqueDates.length > 1 && (
            <Button variant="secondary" className="rounded" onClick={() => setSelectedDates(uniqueDates)}>
              Selecionar todas
            </Button>
          )}
          {selectedDates.length > 0 && (
            <>
              <Button
                variant="outline"
                className="rounded"
                onClick={() => {
                  setSelectedDates([]);
                  setUnifiedGraphData(null);
                  setUnifiedMode(false); // sai do modo unificado ao limpar
                }}
              >
                Limpar seleção
              </Button>

              {/* 🔄 BOTÃO TOGGLE */}
              <Button
                variant={unifiedMode ? "secondary" : "default"}
                className={`rounded ${unifiedMode ? "bg-yellow-500 hover:bg-yellow-600" : ""}`}
                onClick={() => {
                  if (unifiedMode) {
                    // desativar modo unificado
                    setUnifiedGraphData(null);
                    setUnifiedMode(false);
                  } else {
                    // ativar modo unificado
                    setUnifiedGraphData(mergeF1F2DataToCompareUnifiedGraph(filtered));
                    setUnifiedMode(true);
                  }
                }}
              >
                {unifiedMode ? "Voltar ao modo separado" : "Comparar num só gráfico"}
              </Button>
            </>
          )}
        </div>
      </>
    ) : (
      <select
        value={selectedDate || ""}
        onChange={(e) => setSelectedDate(e.target.value)}
        className="mb-4 p-2 border rounded w-full bg-white text-black border-gray-300 dark:bg-zinc-800 dark:text-white dark:border-zinc-600"
      >
        <option value="">Selecione uma data</option>
        {uniqueDates.map((date) => (
          <option key={date} value={date}>
            {date}
          </option>
        ))}
      </select>
    );

  const renderChartImages = () =>
    filtered.map((item) => {
      const imagens = item.pathToChart?.slice(0, 4) || [];
      return (
        <div key={item.step} className="mb-6">
          <h4 className="font-semibold mb-2 dark:text-white">Passo {item.step.replace(/_/g, " ")}</h4>
          {imagens.length === 0 ? (
            <p className="text-red-500">Imagens não encontradas.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {imagens.map((img, i) => (
                <img
                  key={i}
                  src={`${BACKEND_URL}${img}`}
                  alt={`Gráfico ${i + 1}`}
                  className="w-full h-auto rounded-xl shadow border dark:border-zinc-600"
                  onError={(e) => (e.target.style.display = "none")}
                />
              ))}
            </div>
          )}
        </div>
      );
    });

  const renderExerciseAudio = () =>
    filtered.map((item) => {
      const audio = item.pathToRecord;
      return (
        <div key={item.step} className="mb-6">
          <h4 className="font-semibold mb-2 dark:text-white">Passo {item.step.replace(/_/g, " ")}</h4>
          {audio ? (
            <audio controls src={`${BACKEND_URL}${audio}`} className="w-full" />
          ) : (
            <p className="text-red-500">Áudio não encontrado.</p>
          )}
        </div>
      );
    });

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-zinc-900">
        <div className="text-center">
          <div className="animate-spin h-10 w-10 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-xl font-medium text-gray-700 dark:text-gray-300">
            Carregando resultados...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-zinc-900 px-4 py-6">
      <h1 className="text-3xl font-bold text-center mb-6 dark:text-white">
        Resultados de Articulação
      </h1>

      <Card className="p-4 mb-6 shadow-md">
        <div className="flex items-center justify-between">
          <span className="text-lg font-medium dark:text-white">Modo de Comparação</span>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              className="sr-only peer"
              checked={compareMode}
              onChange={() => {
                setCompareMode(!compareMode);
                setSelectedDates([]);
                setUnifiedGraphData(null);
                setUnifiedMode(false);
              }}
            />
            <div
              className={`w-11 h-6 rounded-full transition-colors duration-300 ${
                compareMode ? "bg-green-500" : "bg-gray-300 dark:bg-zinc-700"
              }`}
            >
              <div
                className={`absolute top-0.5 left-[2px] h-5 w-5 rounded-full bg-white shadow transition-transform duration-300 ${
                  compareMode ? "translate-x-full" : ""
                }`}
              />
            </div>
          </label>
        </div>
        {renderDateSelector()}
      </Card>

      {error && (
        <p className="text-red-500 text-center mb-4">Erro: {error.message}</p>
      )}

      {filtered.length > 0 ? (
        <Card className="p-6 shadow-md">
          <CardContent>
            <h2 className="text-xl font-semibold mb-4 dark:text-white">
              Espaço Acústico
            </h2>

            {/* ✅ Indicador visual do modo unificado */}
            {unifiedMode && (
              <div className="text-center mb-4 p-2 bg-green-100 dark:bg-green-800 text-green-700 dark:text-green-300 rounded shadow">
                ✅ Modo "Comparar num só gráfico" ativo
              </div>
            )}

            <DisplayChart groupedData={chartData} />

            <div className="text-sm text-gray-600 dark:text-gray-400 mt-3 m-2">
              {compareMode
                ? unifiedMode
                  ? "Visualizando múltiplas datas num só gráfico."
                  : "Visualizando múltiplas datas."
                : `Visualizando resultados de ${selectedDate}.`}
            </div>

            {!compareMode && (
              <Accordion defaultActiveKey="x">
                <Accordion.Item eventKey="0">
                  <Accordion.Header>📊 Gráficos extraídos do sistema</Accordion.Header>
                  <Accordion.Body>
                    {renderChartImages()}
                  </Accordion.Body>
                </Accordion.Item>

                <Accordion.Item eventKey="1">
                  <Accordion.Header>🎧 Áudios dos exercícios</Accordion.Header>
                  <Accordion.Body>
                    {renderExerciseAudio()}
                  </Accordion.Body>
                </Accordion.Item>
              </Accordion>
            )}

            <div className="mt-6 flex justify-center">
              <Button variant="destructive" className="bg-red-500 hover:bg-red-600 rounded" onClick={handleDelete}>
                Eliminar Todos os Resultados
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="text-center mt-10 text-gray-600 dark:text-gray-300">
          Nenhum resultado disponível para esta data.
        </div>
      )}
    </div>
  );
}

