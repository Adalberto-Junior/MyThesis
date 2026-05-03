import React, { useMemo }  from "react";
import Accordion from "react-bootstrap/Accordion";
import { translateKey } from "./translateKey.jsx";
import { chartConfig } from "./chartConfig.jsx";
import {HistogramChart, F0Chart} from "../../../../component/chart.jsx";
import PropTypes from "prop-types";


export function ChartAccordion({ groupedData }) {
    // console.log("Grouped Data:", groupedData);
  if (!groupedData || Object.keys(groupedData).length === 0) {
    return <p className="text-center mt-2">Nenhum dado disponível</p>;
  }

  return (
    <Accordion alwaysOpen>
      <Accordion.Item eventKey="main">
        <Accordion.Header>Gráficos</Accordion.Header>
        <Accordion.Body>

          {Object.entries(groupedData).map(([chartType, group], chartIndex) => {
            const isRadar = chartType === "radar";
            const title = isRadar ? "Valores Estáticos" : "Valores Não Estáticos";

            return (
              <Accordion.Item eventKey={chartIndex.toString()} key={chartType}>
                <Accordion.Header>{title}</Accordion.Header>
                <Accordion.Body>
                  <Accordion alwaysOpen>
                    {Object.entries(group).map(([groupName, data], idx) => {
                      if (!data || data.length <= 1) return null; // Ignora dados com 1 valor
                      const { labelPrefix, chartComponent: ChartComp } = chartConfig[chartType];
                      return (
                        <Accordion.Item eventKey={idx.toString()} key={groupName}>
                          <Accordion.Header>
                            {labelPrefix} {translateKey(groupName)}
                          </Accordion.Header>
                          <Accordion.Body>
                            <ChartComp data={data} />
                          </Accordion.Body>
                        </Accordion.Item>
                      );
                    })}
                  </Accordion>
                </Accordion.Body>
              </Accordion.Item>
            );
          })}

        </Accordion.Body>
      </Accordion.Item>
    </Accordion>
  );
}

//Dois em dois: Agrupa os dados de radar e linha em um único componente
// export function DisplayChart({ groupedData, filterRadarOnly = false, labels = [], excludeRadarLabels = [], variant = "grid" }) {
//   return (
//     <div className="grid gap-6">
//       {Object.entries(groupedData).map(([chartType, data], idx) => {
//         if (!data || Object.keys(data).length === 0) return null;

//         const isRadar = chartType === "radar";

//         if (isRadar) {
//           const {labelPrefix, chartComponent: ChartComp } = chartConfig.radar;
//           console.log("data: ",data)
//           return (
//             <div key={`${chartType}-${idx}`} className="grid grid-cols-1 md:grid-cols-2 gap-4">
//               {Object.entries(data).map(([dataKey, chartData], i) => (
//                 <div key={`${chartType}-${dataKey}-${i}`} className="bg-white rounded-2xl p-4 shadow w-full h-full min-w-0"
//                 >
//                   <h5 className="text-center mb-2">{labelPrefix} {translateKey(dataKey)}</h5>
//                   <ChartComp data={chartData} />
//                 </div>
//               ))}
//             </div>
//           );
//         }

//         if (chartType === "line") {
//           const { labelPrefix, chartComponent: ChartComponent } = chartConfig.line;
          
//           return (
//             <div key={`${chartType}-${idx}`} className="grid gap-4">
//               {Object.entries(data).map(([dataKey, chartData], i) => (
                
//                 <div key={`${chartType}-${dataKey}-${i}`} className="bg-white dark:bg-zinc-800 p-4 rounded shadow">
//                   <h5 className="text-center mb-2">{labelPrefix} {translateKey(dataKey)}</h5>
//                   <ChartComponent data={chartData} />
//                 </div>
//               ))}
//             </div>
//           );
//         }

//         if (chartType === "acousticSpace"){
//           const { labelPrefix, chartComponent: ChartComponent } = chartConfig.acousticSpace;
//           console.log("chartData: ",data)
//           return(
//             <div key={`${chartType}-${idx}`} className="grid gap-4">
//                 <ChartComponent data={data} />
//             </div>

//           );
//         }

//         if (chartType === "acousticSpaceGrouped"){
//           const { labelPrefix, chartComponent: ChartComponent } = chartConfig.acousticSpaceGrouped;
//           console.log("chartData: ",data)
//           return(
//             <div key={`${chartType}-${idx}`} className="grid gap-4">
//                 <ChartComponent data={data} />
//             </div>

//           );
//         }



       

//         return null;
//       })}
//     </div>
//   );
// }



// DisplayChart.jsx
// export function DisplayChart({
//   groupedData,
//   filterRadarOnly = false,
//   labels = [],
//   excludeRadarLabels = [],
//   variant = "grid",
// }) {
//   if (!groupedData) return null;

//   return (
//     <div className="grid gap-6">
//       {Object.entries(groupedData).map(([chartType, data], idx) => {
//         if (!data || Object.keys(data).length === 0) return null;
//         console.log("DataAntes: ",data)

//         switch (chartType) {
//           case "radar":
//             return renderRadarCharts(data, idx);
//           case "line":
//             return renderLineCharts(data, idx);
//           case "acousticSpace":
//             return renderAcousticChart(data, idx);
//           case "acousticSpaceGrouped":
//             return renderGroupedAcousticChart(data, idx, true);
//           case "acousticSpaceCompared":
//             return renderGroupedAcousticChart(data, idx);
//           case "Boxplot":
//             return renderBoxChart(data, idx,"Boxplot",false);
//           case "PauseDurationBoxplot":
//             return renderBoxChart(data, idx,"PauseDurationBoxplot",false);
//           default:
//             return null;
//         }
//       })}
//     </div>
//   );
// }

export function DisplayChart({
  groupedData,
  comparedValue = false,
  labels = [],
  excludeRadarLabels = [],
  variant = "grid",
}) {
  if (!groupedData) return null;

  

  return (
    <div className="grid gap-6">
      {Object.entries(groupedData).map(([chartType, chartPayload], idx) => {
        if (!chartPayload || Object.keys(chartPayload).length === 0) return null;
        switch (chartType) {
          case "radar":
            return renderRadarCharts(chartPayload, idx);
          case "line":
            return renderLineCharts(chartPayload, idx);
          case "acousticSpace":
            return renderAcousticChart(chartPayload, idx);
          case "acousticSpaceGrouped":
            return renderGroupedAcousticChart(chartPayload, idx, true);
          case "acousticSpaceCompared":
            return renderGroupedAcousticChart(chartPayload, idx);
          case "F0Boxplot":
            return renderF0BoxChart(chartPayload, idx,"Boxplot",false);
          case "Boxplot": {
            const { data, valueKey } = chartPayload;
            // console.log("Data:",data)
            // console.log("valueskeeee: ",valueKey)
            return renderBoxChart(data, idx, valueKey, false);
          }
          case "Intensityplot":
            return IntensityChartWrapper( chartPayload,idx);
          default:
            return null;
        }
      })}
    </div>
  );
}


function renderRadarCharts(data, idx) {
  const { labelPrefix, chartComponent: ChartComp } = chartConfig.radar;

  return (
    <div
      key={`radar-${idx}`}
      className="grid grid-cols-1 md:grid-cols-2 gap-4"
    >
      {Object.entries(data).map(([dataKey, chartData], i) => (
        <div
          key={`radar-${dataKey}-${i}`}
          className="bg-white rounded-2xl p-4 shadow w-full h-full min-w-0"
        >
          <h5 className="text-center mb-2">
            {labelPrefix} {translateKey(dataKey)}
          </h5>
          <ChartComp data={chartData} />
        </div>
      ))}
    </div>
  );
}

function renderLineCharts(data, idx) {
  const { labelPrefix, chartComponent: ChartComponent } = chartConfig.line;

  return (
    <div key={`line-${idx}`} className="grid gap-4">
      {Object.entries(data).map(([dataKey, chartData], i) => (
        <div
          key={`line-${dataKey}-${i}`}
          className="bg-white dark:bg-zinc-800 p-4 rounded shadow"
        >
          <h5 className="text-center mb-2">
            {labelPrefix} {translateKey(dataKey)}
          </h5>
          <ChartComponent data={chartData} />
        </div>
      ))}
    </div>
  );
}

function renderAcousticChart(data, idx) {
  const { chartComponent: ChartComponent } = chartConfig.acousticSpace;

  return (
    <div key={`acousticSpace-${idx}`} className="grid gap-4 items-center justify-center ">
      <ChartComponent data={data} />
    </div>
  );
}

function renderGroupedAcousticChart(data, idx, oneChart = false) {
  if (oneChart) {
    const { chartComponent: ChartComponent } = chartConfig.acousticSpaceGrouped;
    return (
      <div key={`acousticSpaceGrouped-${idx}`} className="grid gap-4">
        <ChartComponent data={data} />
      </div>
    );
  } else {
    const { chartComponent: ChartComponent } = chartConfig.acousticSpaceCompared;
    const entries = Object.entries(data);
    // console.log("data: ", data)
    // console.log("Entries: ", entries)

    // Group entries into pairs
    const pairedEntries = [];
    for (let i = 0; i < entries.length; i += 2) {
      pairedEntries.push(entries.slice(i, i + 2));
    }
    // console.log("paired: ",pairedEntries)

    return (
      <div key={`acousticSpaceGrouped-${idx}`} className="grid gap-6">
        {pairedEntries.map((pair, pairIdx) => (
          <div key={`chart-pair-${pairIdx}`} className="grid grid-cols-2 gap-4">
            {pair.map(([date, dateData]) => (
              <div key={`chart-${date}`} className="border p-4 rounded shadow">
                <h3 className="text-lg font-semibold mb-2">{date.replace(/_/g, " ")}</h3>
                <ChartComponent data={dateData} />
              </div>
            ))}
          </div>
        ))}
      </div>
    );
  }
}


function renderF0BoxChart(data, idx, oneChart = false) {
  const { chartComponent: ChartComponent } = chartConfig.F0Boxplot;

  
  if (oneChart) {
    return (
      <div key={`BoxPlot-${idx}`} className="grid gap-4">
        <ChartComponent data={data} />
      </div>
    );
  } else {
    // data is an array of { id, F0 }
    const entries = data.map(d => [d.id, d.F0]);

    // Group into pairs
    const pairedEntries = [];
    for (let i = 0; i < entries.length; i += 2) {
      pairedEntries.push(entries.slice(i, i + 2));
    }

    return (
      <div key={`BoxPlot-${idx}`} className="grid gap-6">
        {pairedEntries.map((pair, pairIdx) => (
          <div
            key={`chart-pair-${pairIdx}`}
            className={`grid grid-cols-${pair.length} gap-4`}
          >
            {pair.map(([label, f0Values]) => (
              <div key={`chart-${label}`} className="border p-4 rounded shadow">
                <h3 className="text-lg font-semibold mb-2">{label.replace(/_/g, " ")}</h3>
                <ChartComponent data={f0Values} />
              </div>
            ))}
          </div>
        ))}
      </div>
    );
  }
}

// function renderBoxChart(data, idx, valueKey = "F0", oneChart = false) {
//   const { chartComponent: ChartComponent } = chartConfig.Boxplot;

  

//   if (oneChart) {
//     const transformedData = data.reduce((acc, item) => {
//       acc[item.id] = Array.isArray(item[valueKey]) ? item[valueKey] : [item[valueKey]];
//       return acc;
//     }, {});
//     return (
//       <div key={`BoxPlot-${idx}`} className="grid gap-4">
//         <ChartComponent data={transformedData} />
//       </div>
//     );
//   } else {
//     const entries = data.map(d => [d.id, Array.isArray(d[valueKey]) ? d[valueKey] : [d[valueKey]]]);
//     // const entries = data.map(d => [d.id, d[valueKey]]);
//     const pairedEntries = [];
//     for (let i = 0; i < entries.length; i += 2) {
//       pairedEntries.push(entries.slice(i, i + 2));
//     }
//     console.log("ValueKey: ",pairedEntries)
//     return (
//       <div key={`BoxPlot-${idx}`} className="grid gap-6">
//         {pairedEntries.map((pair, pairIdx) => (
//           <div
//             key={`chart-pair-${pairIdx}`}
//             className={`grid grid-cols-${pair.length} gap-4`}
//           >
//             {pair.map(([label, values]) => (
//               <div key={`chart-${label}`} className="border p-4 rounded shadow">
//                 <h3 className="text-lg font-semibold mb-2">{label}</h3>
//                 <ChartComponent data={{ [label]: values }} />
//               </div>
              
//             ))}
//           </div>
//         ))}
//       </div>
//     );
//   }
// }


function renderBoxChart(data, idx, valueKey = "F0", oneChart = false) {
  const { chartComponent: ChartComponent } = chartConfig.Boxplot;

  const normalizeData = (arr) =>
    arr.reduce((acc, item) => {
      acc[item.id] = Array.isArray(item[valueKey])
        ? item[valueKey]
        : [item[valueKey]];
      return acc;
    }, {});

  if (oneChart) {
    const transformedData = normalizeData(data);
    return (
      <div key={`BoxPlot-${idx}`} className="grid gap-6">
        <ChartComponent  parameterName={valueKey} data={transformedData} />
        {/* Histograma único combinando todos os valores */}
         {/* Só mostra histograma se for jitter ou shimmer */}
        {(valueKey === "Jitter" || valueKey === "Shimmer") && (
          <HistogramChart values={Object.values(transformedData).flat()} label={valueKey} />
        )}
        {/* <HistogramChart
          values={Object.values(transformedData).flat()}
          label={valueKey}
        /> */}
      </div>
    );
  } else {
    // Agrupa de 2 em 2
    const paired = [];
    for (let i = 0; i < data.length; i += 2) {
      paired.push(data.slice(i, i + 2));
    }

    return (
      <div key={`BoxPlot-${idx}`} className="grid gap-8">
        {paired.map((subset, pairIdx) => {
          const transformed = normalizeData(subset);
          return (
            <div
              key={`chart-pair-${pairIdx}`}
              className={`grid grid-cols-${Object.keys(transformed).length} gap-6`}
            >
              {Object.entries(transformed).map(([label, values]) => (
                <div
                  key={`chart-${label}-${pairIdx}`}
                  className="border p-4 rounded-xl shadow-md"
                >
                  <h3 className="text-lg font-semibold mb-4">{label.replace(/_/g, " ")}</h3>
                  {/* Boxplot */}
                  <ChartComponent  parameterName={valueKey} data={{ [label]: values }} />
                  {/* Histograma para este conjunto */}
                  <div className="mt-4">
                    {/* <h4 className="text-md font-semibold mb-2">Histograma de {label}</h4> */}
                    {/* <HistogramChart values={values} label={valueKey} /> */}
                    {/* Histograma individual, só se for jitter/shimmer */}
                    {(valueKey === "Jitter" || valueKey === "Shimmer") && (
                      <div className="mt-4">
                        <HistogramChart values={values} label={valueKey} />
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          );
        })}
      </div>
    );
  }
}

// function renderBoxChart(data, idx, valueKey = "F0", oneChart = false) {
//   const { chartComponent: ChartComponent } = chartConfig.Boxplot;
//   console.log("renderBoxChart - data:", data);

//   const normalizeData = (arr) =>
//     arr.reduce((acc, item) => {
//       acc[item.id] = Array.isArray(item[valueKey])
//         ? item[valueKey]
//         : [item[valueKey]];
//       return acc;
//     }, {});

//   if (oneChart) {
//     const transformedData = normalizeData(data);
//     return (
//       <div key={`BoxPlot-${idx}`} className="grid gap-4">
//         <ChartComponent data={transformedData} />
//       </div>
//     );
//   } else {
//     // group into pairs but normalize each subgroup
//     const paired = [];
//     for (let i = 0; i < data.length; i += 2) {
//       paired.push(data.slice(i, i + 2));
//     }

//     return (
//       <div key={`BoxPlot-${idx}`} className="grid gap-6">
//         {paired.map((subset, pairIdx) => {
//           const transformed = normalizeData(subset);
//           return (
//             <div
//               key={`chart-pair-${pairIdx}`}
//               className={`grid grid-cols-${Object.keys(transformed).length} gap-4`}
//             >
//               {Object.entries(transformed).map(([label, values]) => (
//                 <div
//                   key={`chart-${label}-${pairIdx}`}
//                   className="border p-4 rounded shadow"
//                 >
//                   <h3 className="text-lg font-semibold mb-2">{label}</h3>
//                   <ChartComponent data={{ [label]: values }} />
//                 </div>
//               ))}
//             </div>
//           );
//         })}
//       </div>
//     );
//   }
// }


function IntensityChartWrapper(data, idx) {
  const { chartComponent: ChartComponent } = chartConfig.Intensityplot;
  // console.log("IntensityChartWrapper: ", data);
  if (!data || data.length === 0) {
    return (
      <div key={`IntensityChartWrapper-${idx}`} className="grid gap-6">
        <h2>Nenhum dado encontrado</h2>
      </div>
    );
  }

  return (
    <div className="grid gap-6">
      {data.map((d, idx) => (
        <div key={`Intensityplot-${d.id || idx}`} className="grid gap-4">
          <h3 className="text-lg font-semibold">Gráfico de Intensidade – {d.id.replace(/_/g, " ")}</h3>
          <ChartComponent data={d.Intensidade} width={800} height={300} />
        </div>
      ))}
    </div>
  );
}



export function RenderF0LineChart({data, idx, oneChart = false}) {
  if (!data || data.length === 0)  return <div>Nenhum dado para exibir</div>;
  // console.log("RenderF0LineChart - data:", data);

  if (oneChart) {
    // Mostra todos os F0 num único gráfico (pode ser útil para comparação)
    const combined = data.flatMap((d) =>
      d.F0.map((val, i) => ({ id: d.id, timeIndex: i, f0: val }))
    );

    return (
      <div key={`F0Chart-${idx}`} className="grid gap-4">
        <F0Chart
          f0={combined.map((d) => d.f0)}
          timeStepMs={5} // altera se o teu frame period não for 5 ms
        />
      </div>
    );
  } else {

    // Divide os dados em pares para mostrar lado a lado
    const pairedEntries = [];
    for (let i = 0; i <  data.F0Boxplot.length; i += 2) {
      pairedEntries.push(data.F0Boxplot.slice(i, i + 2));
    }

    // console.log("pairedEntries: ", pairedEntries);

    return (
      <div key={`F0Chart-${idx}`} className="grid gap-6">
        {pairedEntries.map((pair, pairIdx) => (
          <div
            key={`chart-pair-${pairIdx}`}
            className={`grid grid-cols-${pair.length} gap-4`}
          >
            {pair.map((d) => (
              <div key={`chart-${d.id}`} className="border p-4 rounded shadow">
                <h3 className="text-lg font-semibold mb-2">{d.id.replace(/_/g, " ")}</h3>
                <F0Chart
                  f0={d.F0}
                  timeStepMs={5} // altera se necessário
                />
              </div>
            ))}
          </div>
        ))}
      </div>
    );
  }
}