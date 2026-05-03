import React, { useEffect, useState } from "react";
import api from "../../../api";
import { useParams } from "react-router-dom";
import Accordion from "react-bootstrap/Accordion";
import 'bootstrap/dist/css/bootstrap.min.css';
import BarChart from "../../../component/barChart.jsx";
import RadarChart from "../../../component/radarChart.jsx";

const keyTranslations = {
  static_result: "Resultados Estáticos",
  no_static_result: "Resultados não Estáticos",
  // Adicione traduções conforme necessário
};

function translateKey(key) {
  return keyTranslations[key] || key.replace(/_/g, " ");
}

export default function ArticulationResult() {
  const [results, setResults] = useState([]);
  const [selectedDate, setSelectedDate] = useState(null);
  const { id } = useParams();

  useEffect(() => {
    api.get(`/utente/${id}/analise/articulacao`)
      .then(res => {
        setResults(res.data);
        if (res.data.length) setSelectedDate(res.data[0].date);
      })
      .catch(console.error);
  }, [id]);

  const uniqueDates = [...new Set(results.map(r => r.date))];
  const filtered = results.filter(r => r.date === selectedDate);

  // Agrupa dados estáticos para Radar
  function buildRadarData(staticArr) {
    const groups = {};
    staticArr.forEach(obj => {
      Object.entries(obj).forEach(([k, v]) => {
        const prefix = k.replace(/_\d+$/, '');
        const num = parseFloat(v[0]);
        groups[prefix] = groups[prefix] || [];
        groups[prefix].push(num);
      });
    });
    return Object.entries(groups).map(([axis, vals]) => ({
      axis,
      value: vals.reduce((a, b) => a + b, 0) / vals.length
    }));
  }

  // Agrupa dados não estáticos para Barras
  function buildBarData(nonStaticArr) {
    const result = {};
    nonStaticArr.forEach(obj => {
      Object.entries(obj).forEach(([k, arr]) => {
        result[k] = (arr || []).map(x => parseFloat(x));
      });
    });
    return result;
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-zinc-900 px-4">
      <div className="flex-1 p-1">
        <div className="w-full max-w-xl bg-white dark:bg-zinc-800 shadow-md rounded-lg p-6">
          <h1 className="text-2xl font-bold text-center mb-5">Resultados de Articulação</h1>

          <select
            className="mb-4 p-2 border rounded w-full"
            value={selectedDate || ''}
            onChange={e => setSelectedDate(e.target.value)}
          >
            {uniqueDates.map((d, i) => (
              <option key={i} value={d}>{d}</option>
            ))}
          </select>

          {filtered.length ? (
            <Accordion alwaysOpen>
              {filtered.map((item, idx) => {
                const radarData = buildRadarData(item.static_result || []);
                const barGroups = buildBarData(item.no_static_result || []);

                return (
                  <Accordion.Item eventKey={idx.toString()} key={idx}>
                    <Accordion.Header>{`Step ${idx + 1}`}</Accordion.Header>
                    <Accordion.Body>

                      {/* Dados Numéricos */}
                      <div className="mb-6">
                        <h2 className="text-lg font-semibold mb-2">Números</h2>
                        {/** Reutilize seu Accordion recursivo aqui se quiser **/}
                      </div>

                      {/* Radar Chart */}
                      <div className="mb-6">
                        <h2 className="text-lg font-semibold mb-2">Radar (Estáticos)</h2>
                        <RadarChart data={radarData} />
                      </div>

                      {/* Bar Charts */}
                      <div>
                        <h2 className="text-lg font-semibold mb-2">Barras (Não Estáticos)</h2>
                        {Object.entries(barGroups).map(([key, vals]) => (
                          <div key={key} className="mb-4">
                            <h3 className="font-medium mb-1">{translateKey(key)}</h3>
                            <BarChart data={vals} />
                          </div>
                        ))}
                      </div>

                    </Accordion.Body>
                  </Accordion.Item>
                );
              })}
            </Accordion>
          ) : (
            <p className="text-center mt-5">Nenhum dado disponível para essa data.</p>
          )}

        </div>
      </div>
    </div>
  );
}
