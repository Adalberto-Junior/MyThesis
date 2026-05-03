import React, { useEffect, useState } from "react";
import api from "../../../../api";
import { useParams } from "react-router-dom";
import Accordion from "react-bootstrap/Accordion";
import 'bootstrap/dist/css/bootstrap.min.css';
import { RecursiveAccordion } from "../chartConfiguraction/RecursiveAccordion.jsx";
import {chartConfig} from "../chartConfiguraction/chartConfig.jsx";
import {groupChartData, groupBBEonBBEoffData, groupNotBBEonBBEoffData,groupPhonactionData} from "../chartConfiguraction/groupChartData.jsx";
import {ChartAccordion, DisplayChart} from "../chartConfiguraction/ChartAccordion.jsx";
import {RadarChart, BarChart, StaticBarChart} from "../../../../component/chart.jsx"

const keyTranslations = {
    static_result: "Resultados Estáticos",
    no_static_result: "Resultados não Estáticos",
    "avg_BBEon_1": "Média BBEon 1",
    "avg_BBEon_2": "Média BBEon 2",
    "avg_BBEon_3": "Média BBEon 3",
    "avg_BBEon_4": "Média BBEon 4",
    $oid: "ID do Objeto",
    id: "Identificador",
    date: "Data",
    // Adicione outros conforme necessário
};

function translateKey(key) {
    return keyTranslations[key] || key.replace(/_/g, " ");
}


export default function PhonotionResult() {
  const [results, setResults] = useState([]);
  const [selectedDate, setSelectedDate] = useState(null);
  const { id } = useParams();
  const BACKEND_URL = "http://localhost:5000";

  useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await api.get(`/utente/${id}/analise/fonacao`);
                setResults(response.data);
                if (response.data.length > 0) {
                  setSelectedDate(response.data[response.data.length - 1].date);
                }
            } catch (error) {
                console.error("Erro ao buscar dados:", error);
            }
        };
        fetchData();
    }, [id]);

  const handleDelete = async () => {
    const typeOfProcessing = filtered.find(item => item.date === selectedDate)?.processing_type;
    if (!typeOfProcessing) return;
    const selectedDate_ = selectedDate;
    try {
      if (!window.confirm(`Tem certeza que deseja eliminar todos os resultados desta data: ${selectedDate_}?`)) return;

      await api.delete(`/utente/${id}/analise/${typeOfProcessing}/${selectedDate}`);
      setResults((prevResults) => prevResults.filter((res) => res.date !== selectedDate));
      if (filtered.length === 0) {
        setSelectedDate(null);
      }
      alert(`Resultados da data ${selectedDate_} eliminado com sucesso!`);
      window.location.reload();
    } catch (error) {
      console.error("Erro ao deletar dados:", error);
      alert("Erro ao eliminar os resultados. Tente novamente.");
    }
  };

  const handleDeleteByResultId = async (resultId) => {
    try {
      if (!window.confirm("Tem certeza que deseja eliminar este resultado?")) return;

      await api.delete(`/utente/${id}/analise/${resultId.$oid || resultId}`);
      setResults((prevResults) => prevResults.filter((res) => res._id !== resultId));
      if (filtered.length === 0) {
        setSelectedDate(null);
      }
      alert("Resultado eliminado com sucesso!");
      window.location.reload();
    } catch (error) {
      console.error("Erro ao deletar dados:", error);
      alert("Erro ao eliminar o resultado. Tente novamente.");
    }
  };

  const uniqueDates = [...new Set(results.map((res) => res.date))];
  const filtered = results.filter((res) => res.date === selectedDate);

  const radarLabels = ['bbeon', 'bbeoff'];

  const allRadarGroupedData = filtered.reduce((acc, item, index) => {
    const staticResult = item.static_result || [];
    // console.log("Static Result: ", staticResult);
    const grouped = groupPhonactionData(staticResult, chartConfig);

    Object.entries(grouped).forEach(([type, charts]) => {
      if (!acc[type]) acc[type] = {};
      Object.entries(charts).forEach(([label, data]) => {
        // Adiciona passo no rótulo para distinção visual
        // acc[type][`${label} (Passo ${index + 1})`] = data;
        acc[type][`${label} (Passo ${item.step})`] = data;
      });
    });

    return acc;
  }, {});


  return (
    <div className="min-h-screen min-w-screen items-center justify-center bg-gray-100 dark:bg-zinc-900 px-4">
      <div className="flex-1 p-1">
        <div className="text-4xl font-bold text-center mb-5 p-3 text-gray-900 dark:text-white">Resultados de Fonação</div>

        <select
          className="mb-4 p-2 border rounded w-full bg-white text-black border-gray-300 dark:bg-zinc-800 dark:text-white dark:border-zinc-600"
          value={selectedDate || ''}
          onChange={e => setSelectedDate(e.target.value)}
        >
          {uniqueDates.map((d, i) => (
            <option key={i} value={d}>{d}</option>
          ))}
        </select>

        {filtered.length ? (
          <div className="w-full bg-gray-100 dark:bg-zinc-900 rounded-lg p-6">
            <div className="w-full flex flex-col md:flex-row gap-4 items-start">
              <div className="w-full md:basis-2/6 bg-gray-100 dark:bg-zinc-900 rounded-lg p-6">
                <div className="w-full bg-white dark:bg-zinc-800 shadow-md rounded-lg p-6">
                  <h2 className="text-lg font-semibold mb-3">Dados Numéricos Relevantes</h2>
                  {filtered.map((item, idx) => {
                    const staticResult = item.static_result || [];
                    const camposImportantes = ["avg Shimmer", "avg Jitter", "avg apq", "avg ppq","avg DF0", "avg DDF0","avg logE"];
                    const dadosRelevantes = staticResult.filter(obj => camposImportantes.includes(Object.keys(obj)[0]));
                    const prioridade = campo => {
                      if (campo.includes("DDF")) return 3;
                      if (campo.includes("DF")) return 2;
                      return 1;
                    };

                    dadosRelevantes.sort((a, b) => {
                      const chaveA = Object.keys(a)[0];
                      const chaveB = Object.keys(b)[0];
                      return prioridade(chaveA) - prioridade(chaveB);
                    });

                    if (dadosRelevantes.length === 0) return null;
                    return (
                      <div key={idx} className="mb-6">
                        <h3 className="text-md font-bold mb-2">Passo {item.step}</h3>
                        <table className="min-w-full bg-white border border-gray-300 dark:bg-zinc-800 dark:border-zinc-600">
                          <thead>
                            <tr className="bg-green-300 dark:bg-gray-500 sticky top-0 z-10">
                              <th className="border border-gray-400 dark:border-zinc-500 px-4 py-2 text-left">Parâmetro</th>
                              <th className="border border-gray-400 dark:border-zinc-500 px-4 py-2 text-left">Valor</th>
                            </tr>
                          </thead>
                          <tbody>
                            {dadosRelevantes.map((obj, idxs) => {
                              const chave = Object.keys(obj)[0];
                              let valor = obj[chave];
                              if (typeof valor !== 'number') valor = parseFloat(valor) || "N/A";
                              return (
                                <tr key={idxs} className="odd:bg-gray-100 odd:dark:bg-gray-300">
                                  <td className="border border-gray-400 dark:border-zinc-500 px-4 py-2">{translateKey(chave)}</td>
                                  <td className="border border-gray-400 dark:border-zinc-500 px-4 py-2">
                                    {typeof valor === 'number' && !isNaN(valor) ? valor.toFixed(3) : 'N/A'}
                                  </td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    );
                  })}
                </div>
              </div>
              <div className="w-full md:basis-4/5  bg-white dark:bg-zinc-700 p-6 rounded shadow">
                <h2 className="text-xl font-bold mb-4">Gráficos</h2>
                <h3 className="text-md font-semibold mb-3"></h3>
                {/* <div className="grid grid-cols-1 md:grid-cols-2  "> */}
                  {Object.keys(allRadarGroupedData).map((type) => (
                    <div key={type} className="w-full min-w-0">
                      <DisplayChart
                        groupedData={{ [type]: allRadarGroupedData[type] }}
                        filterRadarOnly={false}
                        labels={radarLabels}
                      />
                    </div>
                  ))}
                {/* Outros Gráficos de Radar */}
                {/* <Accordion defaultActiveKey="x" className="mt-6">
                  <Accordion.Item eventKey="0">
                    <Accordion.Header>Outros Gráficos de Radar</Accordion.Header>
                    <Accordion.Body>
                      {filtered.map((item, idx) => {
                        const staticResult = item.static_result || [];
                        const groupedData = groupNotBBEonBBEoffData(staticResult, chartConfig);
                        return (
                          <div key={idx} className="mb-6">
                            <h4 className="font-semibold mb-1">Passo {item.step}</h4>
                            <DisplayChart groupedData={groupedData} filterRadarOnly={true} excludeRadarLabels={radarLabels} />
                          </div>
                        );
                      })}
                    </Accordion.Body>
                  </Accordion.Item>
                </Accordion> */}

                <Accordion defaultActiveKey="x" className="mt-6">
                  <Accordion.Item eventKey="0">
                    <Accordion.Header> Gráficos de valores não estáticos</Accordion.Header>
                    <Accordion.Body>
                      {filtered.map((item, idx) => {
                        const nonStaticResult = item.no_static_result || [];
                        const groupedData = groupChartData([], nonStaticResult, chartConfig, 40);
                        // console.log("grouped data: ", groupedData)
                        return (
                          <div key={idx} className="mb-6">
                            <h4 className="font-semibold mb-1">Passo {item.step}</h4>
                            <DisplayChart groupedData={groupedData} />
                          </div>
                        );
                      })}
                    </Accordion.Body>
                  </Accordion.Item>
                </Accordion>

                <Accordion defaultActiveKey="x" className="mt-6">
                  <Accordion.Item eventKey="0">
                    <Accordion.Header>Gráficos extraídos do sistema</Accordion.Header>
                    <Accordion.Body>
                      {filtered.map((item, idx) => {
                        const imagens = item.pathToChart?.slice(0, 4).map(img => `${BACKEND_URL}${img}`) || [];
                        const imagensComErro = new Set(); // para rastrear imagens que falharam

                        const todasFalharam = imagens.length > 0 && imagensComErro.size === imagens.length;

                        return (
                          <div key={idx} className="mb-6">
                            <h4 className="font-semibold mb-2">Passo {item.step}</h4>

                            {/* Se não há imagens ou todas falharam */}
                            {imagens.length === 0 ? (
                              <p className="text-red-500">Imagens não encontradas para este passo.</p>
                            ) : (
                              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-4">
                                {imagens.map((src, i) => (
                                  <img
                                    key={i}
                                    src={src}
                                    alt={`Gráfico ${i + 1} do Passo ${item.step}`}
                                    className="w-full h-auto rounded border shadow-sm dark:border-zinc-600"
                                    onError={(e) => {
                                      imagensComErro.add(i);
                                      e.target.style.display = "none";

                                      // Se todas falharem, força re-render para mostrar a mensagem
                                      if (imagensComErro.size === imagens.length) {
                                        e.target.closest("div").innerHTML =
                                          '<p class="text-red-500">Imagens não encontradas para este passo.</p>';
                                      }
                                    }}
                                  />
                                ))}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </Accordion.Body>
                  </Accordion.Item>
                </Accordion>
              
              </div>
            </div>

               {/* Dados Adicionais em Accordion */}
            <div className="w-full mt-6"></div>
            <div className="bg-white dark:bg-zinc-700 p-6 rounded shadow">
                <h2 className="text-lg font-semibold mb-3">Dados Detalhados</h2>
                <Accordion alwaysOpen>
                  { filtered.map((item, idx) => {
                     return (
                      <Accordion.Item eventKey={`extra-${idx}`} key={idx}>
                        <Accordion.Header>{`Passo ${item.step}`}</Accordion.Header>
                        <Accordion.Body>
                           <RecursiveAccordion data={item} />
                        </Accordion.Body>
                      </Accordion.Item>
                     );
                   })}
                 </Accordion>
              </div>

            <div className="w-full mt-6 flex justify-center">
              <button
                className="mb-4 bg-red-500 text-white px-6 py-2 rounded hover:bg-red-600 transition-colors dark:bg-red-700 dark:hover:bg-red-800"
                onClick={() => handleDelete()}
              >
                Eliminar Todos os Resultados
              </button>
            </div>
          </div>
        ) : (
          <div className="w-full bg-gray-100 dark:bg-zinc-900 rounded-lg p-9">
            <p className="text-center mt-5 text-3xl dark:text-white">Nenhum dado disponível para essa data.</p>
          </div>
        )}
      </div>
    </div>
  );
}