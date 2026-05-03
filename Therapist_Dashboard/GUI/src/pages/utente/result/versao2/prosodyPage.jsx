import React, { useEffect, useState, useMemo } from "react";
import { useParams } from "react-router-dom";
import api from "../../../../api";
import Accordion from "react-bootstrap/Accordion";
import "bootstrap/dist/css/bootstrap.min.css";

import { Card, CardContent, CardHeader, CardTitle } from "../../../../components/ui/card";
import { Button } from "../../../../components/ui/button";

import { RenderF0LineChart, DisplayChart } from "../chartConfiguraction/ChartAccordion.jsx";
import {
  groupF0ToBoxplot,
  groupFeatureToBoxplot,
  groupDataToIntensityplot,
} from "../chartConfiguraction/groupChartData.jsx";

const BACKEND_URL = "http://localhost:5000";

export default function ProsodyResultPage() {
  const { id } = useParams();
  const [results, setResults] = useState([]);
  const [selectedDate, setSelectedDate] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  /** 🔎 Buscar resultados da API */
  useEffect(() => {
    async function fetchResults() {
      try {
        const response = await api.get(`/utente/${id}/analise/prosodia`);
        const data = Array.isArray(response.data) ? response.data : [];
        setResults(data);
        if (data.length > 0) {
          setSelectedDate(data[data.length - 1].date);
        }
      } catch (err) {
        console.error(err);
        setError("Erro ao carregar resultados de prosódia.");
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
  const f0Data = useMemo(() => groupF0ToBoxplot(filtered), [filtered]);
  const pauseDurations = useMemo(
    () => groupFeatureToBoxplot(filtered, "pausedurations"),
    [filtered]
  );
  const intensityData = useMemo(() => groupDataToIntensityplot(filtered), [filtered]);

  // console.log("Intensity Data: ", intensityData);
  // console.log("filtered: ", filtered);

  /** 🗑️ Eliminar resultados */
  const handleDelete = async () => {
    const typeOfProcessing = filtered.find((item) => item.date === selectedDate)?.processing_type;
    if (!typeOfProcessing) return;
    if (!window.confirm(`Tem certeza que deseja eliminar os resultados de ${selectedDate}?`)) return;

    try {
      await api.delete(`/utente/${id}/analise/${typeOfProcessing}/${selectedDate}`);
      setResults((prev) => prev.filter((res) => res.date !== selectedDate));
      setSelectedDate(uniqueDates.length > 1 ? uniqueDates[uniqueDates.length - 2] : "");
      alert(`Resultados de ${selectedDate} eliminados com sucesso!`);
    } catch (err) {
      console.error(err);
      alert("Erro ao eliminar os resultados. Tente novamente.");
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
        <div key={`charts-${item.step}`} className="mb-6">
          <h4 className="font-semibold mb-2 dark:text-white">Passo {item.step}</h4>
          {imagens.length === 0 ? (
            <p className="text-red-500">Imagens não encontradas para este passo.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {imagens.map((img, i) => (
                <img
                  key={`img-${item.step}-${i}`}
                  src={`${BACKEND_URL}${img}`}
                  alt={`Gráfico ${i + 1} - Passo ${item.step}`}
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
      <div key={`audio-${item.step}`} className="mb-6">
        <h4 className="font-semibold mb-2 dark:text-white">Passo {item.step}</h4>
        {item.pathToRecord ? (
          <audio controls src={`${BACKEND_URL}${item.pathToRecord}`} className="w-full" />
        ) : (
          <p className="text-red-500">Áudio não encontrado para este passo.</p>
        )}
      </div>
    ));



const SpeechRateMetrics = ({ filtered }) => {
  return (
    <Card className="shadow-lg rounded-2xl">
      <CardHeader className="border-b">
        <CardTitle className="text-2xl font-bold text-center dark:text-white">
          Métricas de Velocidade e Fluência da Fala
        </CardTitle>
      </CardHeader>

      <CardContent className="overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <thead className="sticky top-0 z-10 bg-green-300 dark:bg-gray-700">
            <tr>
              <th className="px-4 py-2 text-left border-b border-gray-300 dark:border-zinc-600">
                Métrica
              </th>
              <th className="px-4 py-2 text-center border-b border-gray-300 dark:border-zinc-600">
                Valor
              </th>
              <th className="px-4 py-2 text-center border-b border-gray-300 dark:border-zinc-600">
                Unidade
              </th>
            </tr>
          </thead>

          <tbody>
            {filtered.map((data) => {
              const speechRateResults =
                data.no_static_result?.filter((item) => item.SpeechRate) || [];

              if (speechRateResults.length === 0) return null;

              return (
                <React.Fragment key={data.step}>
                  {/* Cabeçalho de cada passo */}
                  <tr className="bg-green-200 dark:bg-green-600 font-semibold">
                    <td
                      className="px-4 py-2 border-y border-gray-300 dark:border-zinc-600"
                      colSpan={3}
                    >
                      Passo: {data.step.replace(/_/g, " ")}
                    </td>
                  </tr>

                  {speechRateResults.map((result, rIdx) => {
                    const metrics = result.SpeechRate;

                    return Object.entries(metrics)
                      .filter(([_, value]) => !Array.isArray(value))
                      .map(([metric, value], idx) => {
                        const unitMatch = metric.match(/\((.*?)\)/);
                        const unit = unitMatch ? unitMatch[1] : "";

                        const toTitleCase = (str) =>
                          str
                            .toLowerCase()
                            .replace(/\b\p{L}/gu, (l) => l.toUpperCase())
                            .trim();

                        const cleanedName = toTitleCase(
                          metric.replace(/\(.*?\)/g, "").replace(/_/g, " ")
                        );

                        return (
                          <tr
                            key={`${data.step}-${rIdx}-${idx}`}
                            className="odd:bg-gray-50 odd:dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                          >
                            <td className="px-4 py-2 border-b border-gray-200 dark:border-zinc-700">
                              {cleanedName}
                            </td>
                            <td className="px-4 py-2 text-center border-b border-gray-200 dark:border-zinc-700">
                              {value}
                            </td>
                            <td className="px-4 py-2 text-center border-b border-gray-200 dark:border-zinc-700">
                              {unit}
                            </td>
                          </tr>
                        );
                      });
                  })}
                </React.Fragment>
              );
            })}
          </tbody>
        </table>
      </CardContent>
    </Card>
  );
}


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
        Resultados de Prosódia
      </h1>

      <Card className="p-4 mb-6 shadow-md">{renderDateSelector()}</Card>

      {error && <p className="text-red-500 text-center mb-4">{error}</p>}

      {filtered.length > 0 ? (
        <Card className="p-6 shadow-md">
          <CardContent>
            {/* F0 ao longo do tempo */}
            <h2 className="text-xl font-semibold mb-4 dark:text-white">F0 ao longo do tempo</h2>
            <RenderF0LineChart data={f0Data} idx={1} />

            {/* Intensidade */}
            {/* <h2 className="text-xl font-semibold mt-6 mb-3 dark:text-white">Intensidade</h2> */}
            <DisplayChart groupedData={intensityData} />

            {/* Duração de pausa */}
            <h2 className="text-xl font-semibold mt-6 mb-3 dark:text-white">Duração de pausa</h2>
            <DisplayChart groupedData={pauseDurations} />

            {/* Tabela de métricas */}
            <SpeechRateMetrics filtered={filtered} />


            <Accordion defaultActiveKey="x" className="mb-6 mt-6">
              <Accordion.Item eventKey="0">
                <Accordion.Header>📊 Gráficos Extraídos do Sistema</Accordion.Header>
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
          Nenhum resultado disponível para essa data.
        </div>
      )}
    </div>
  );
}
