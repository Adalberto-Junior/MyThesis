import { useEffect, useState, useMemo } from "react";
import { useParams } from "react-router-dom";
import api from "../../../../api";
import { Card, CardContent } from "../../../../components/ui/card";
import Accordion from "react-bootstrap/Accordion";
import { Button } from "../../../../components/ui/button";
import "bootstrap/dist/css/bootstrap.min.css";

import {
  groupFeatureToBoxplot,
  groupDataToIntensityplot,
  groupF0ToBoxplot,
} from "../chartConfiguraction/groupChartData.jsx";
import { DisplayChart } from "../chartConfiguraction/ChartAccordion.jsx";

const BACKEND_URL = "http://localhost:5000";

export default function PhonotionResultPage() {
  const { id } = useParams();
  const [results, setResults] = useState([]);
  const [selectedDate, setSelectedDate] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  /** 🔎 Buscar resultados da API */
  useEffect(() => {
    async function fetchResults() {
      try {
        const res = await api.get(`/utente/${id}/analise/fonacao`);
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
  const filtered = useMemo(
    () => results.filter((res) => res.date === selectedDate),
    [results, selectedDate]
  );

  /** 📊 Dados dos gráficos */
  const jitterData = useMemo(() => groupFeatureToBoxplot(filtered, "Jitter"), [filtered]);
  const shimmerData = useMemo(() => groupFeatureToBoxplot(filtered, "Shimmer"), [filtered]);
  const intensityData = useMemo(() => groupDataToIntensityplot(filtered), [filtered]);
  const f0Data = useMemo(() => groupF0ToBoxplot(filtered), [filtered]);

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
  const renderDateSelector = () => (
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

  /** 🖼️ Renderização de imagens */
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

  /** 🔊 Renderização de áudio */
  const renderExerciseAudio = () =>
    filtered.map((item) => (
      <div key={item.step} className="mb-6">
        <h4 className="font-semibold mb-2 dark:text-white">Passo {item.step.replace(/_/g, " ")}</h4>
        {item.pathToRecord ? (
          <audio controls src={`${BACKEND_URL}${item.pathToRecord}`} className="w-full" />
        ) : (
          <p className="text-red-500">Áudio não encontrado.</p>
        )}
      </div>
    ));



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
        Resultados de Fonação
      </h1>

      <Card className="p-4 mb-6 shadow-md">{renderDateSelector()}</Card>

      {error && <p className="text-red-500 text-center mb-4">Erro: {error.message}</p>}

      {filtered.length > 0 ? (
        <Card className="p-6 shadow-md">
          <CardContent>
            <h2 className="text-xl font-semibold mb-4 dark:text-white">Jitter</h2>
            <DisplayChart groupedData={jitterData} />

            <h2 className="text-xl font-semibold mb-4 mt-6 dark:text-white">Shimmer</h2>
            <DisplayChart groupedData={shimmerData} />

            <h2 className="text-xl font-semibold mb-4 mt-6 dark:text-white">F0</h2>
            <DisplayChart groupedData={f0Data} />

            <h2 className="text-xl font-semibold mb-4 mt-6 dark:text-white">
              Tempo Máximo de Fonação
            </h2>
            <div className="overflow-x-auto mb-6">
              <table className="min-w-full border-collapse border border-gray-300 dark:border-zinc-500">
                <thead>
                  <tr className="bg-green-300 dark:bg-zinc-700">
                    <th className="border px-4 py-2">Passo</th>
                    <th className="border px-4 py-2 text-center">Valor</th>
                    <th className="border px-4 py-2 text-center">Medida</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((data) => (
                    <tr key={`tmf-${data.step}`} className="odd:bg-gray-50 odd:dark:bg-zinc-700">
                      <td className="border px-4 py-2">{data.step.replace(/_/g, " ")}</td>
                      <td className="border px-4 py-2 text-center">
                        {data.static_result
                          ?.filter((item) => item.TMF !== undefined)
                          .map((item, idx) => (
                            <div key={idx}>{item.TMF.toFixed(3)}</div>
                          ))}
                      </td>
                      <td className="border px-4 py-2 text-center">Segundos</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <Accordion defaultActiveKey="x" className="mb-6">
              <Accordion.Item eventKey="0">
                <Accordion.Header>📊 Gráficos Extraídos</Accordion.Header>
                <Accordion.Body>{renderChartImages()}</Accordion.Body>
              </Accordion.Item>

              <Accordion.Item eventKey="1">
                <Accordion.Header>🎧 Áudios dos Exercícios</Accordion.Header>
                <Accordion.Body>{renderExerciseAudio()}</Accordion.Body>
              </Accordion.Item>
            </Accordion>

            <div className="mt-6 flex justify-center">
              <Button
                variant="destructive"
                className="bg-red-500 hover:bg-red-600 rounded"
                onClick={handleDelete}
              >
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
