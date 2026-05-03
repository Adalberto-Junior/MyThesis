// Accordion Recursivo
import React from "react";
import Accordion from "react-bootstrap/Accordion";
import { translateKey } from "./translateKey.jsx";

// export function RecursiveAccordion({ data }) {
//   if (!data || Object.keys(data).length === 0) {
//     return <p className="text-center mt-2">Nenhum dado disponível</p>;
//   }
//   return (
//     <Accordion alwaysOpen>
//       {Object.entries(data).map(([key, value], index) => (
//         <Accordion.Item eventKey={index.toString()} key={index}>
//           {key !== "_id" && key !== "date" && key !== "user" && key !== "recording" && key !== "processing_type" && key !== "step" && (
//             <>
//               <Accordion.Header>{translateKey(key)}</Accordion.Header>
//               <Accordion.Body>
//                 {typeof value === "object" && value !== null ? (
//                   Array.isArray(value) ? (
//                     value.map((item, subIndex) => (
//                       <div key={subIndex} className="border p-2 rounded">
//                         {typeof item === "object" && item !== null ? (
//                           <RecursiveAccordion data={item} />
//                         ) : (
//                           item.toString()
//                         )}
//                       </div>
//                     ))
//                   ) : (
//                     <RecursiveAccordion data={value} />
//                   )
//                 ) : (
//                   value.toString()
//                 )}
//               </Accordion.Body>
//             </>
//           )}
//         </Accordion.Item>
//       ))}
//     </Accordion>
//   );
// }

export function RecursiveAccordion({ data }) {
  if (!data || Object.keys(data).length === 0) {
    return <p className="text-center mt-2">Nenhum dado disponível</p>;
  }

  return (
    <Accordion alwaysOpen>
      {Object.entries(data).map(([key, value], index) => {
        if (key === "_id" || key === "date" || key === "user" || key === "recording" || key === "processing_type" || key === "step") {
          return null;
        }

        // Renderizar static_result como tabela
        if (key === "static_result" && Array.isArray(value)) {
          return (
            <Accordion.Item eventKey={`static-${index}`} key={`static-${index}`}>
              <Accordion.Header>{translateKey(key)}</Accordion.Header>
              <Accordion.Body>
                {/* <table className="min-w-full bg-white dark:bg-zinc-800 border border-gray-300 dark:border-zinc-600">
                  <thead>
                    <tr className="bg-gray-200 dark:bg-gray-500">
                      <th className="border-b p-2 text-left">Parâmetro</th>
                      <th className="border-b p-2 text-left">Valor</th>
                    </tr>
                  </thead>
                  <tbody>
                    {value.map((item, i) => {
                      const chave = Object.keys(item)[0];
                      const val = item[chave];
                      return (
                        <tr key={i}>
                          <td className="border-b p-2">{translateKey(chave)}</td>
                          <td className="border-b p-2">
                            {typeof val === "number" ? val.toFixed(2) : val.toString()}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table> */}
                {/* <table className="min-w-full border-collapse border border-gray-400 dark:border-zinc-500">
                  <thead>
                    <tr className="bg-gray-200 dark:bg-gray-500">
                      <th className="border border-gray-400 dark:border-zinc-500 px-4 py-2 text-left">Parâmetro</th>
                      <th className="border border-gray-400 dark:border-zinc-500 px-4 py-2 text-left">Valor</th>
                    </tr>
                  </thead>
                  <tbody>
                    {value.map((item, i) => {
                      const chave = Object.keys(item)[0];
                      const val = item[chave];
                      return (
                        <tr key={i}>
                          <td className="border border-gray-400 dark:border-zinc-500 px-4 py-2">{translateKey(chave)}</td>
                          <td className="border border-gray-400 dark:border-zinc-500 px-4 py-2">
                            {typeof val === "number" ? val.toFixed(2) : val.toString()}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table> */}

                <div className="overflow-y-auto max-h-80">
                  <table className="min-w-full border-collapse border border-gray-400 dark:border-zinc-500">
                    <thead>
                      <tr className="bg-green-300 dark:bg-gray-500 sticky top-0 z-10">
                        <th className="border border-gray-400 dark:border-zinc-500 px-4 py-2 text-left">Índice</th>
                        <th className="border border-gray-400 dark:border-zinc-500 px-4 py-2 text-left">Parâmetro</th>
                        <th className="border border-gray-400 dark:border-zinc-500 px-4 py-2 text-left">Valor</th>
                      </tr>
                    </thead>
                    <tbody>
                      {value.map((item, i) => {
                        const chave = Object.keys(item)[0];
                        const val = item[chave];
                        return (
                          <tr key={i} className="odd:bg-gray-100 odd:dark:bg-gray-300">
                            <td className="border border-gray-400 dark:border-zinc-500 px-4 py-2">{i + 1}</td>
                            <td className="border border-gray-400 dark:border-zinc-500 px-4 py-2">{translateKey(chave)}</td>
                            <td className="border border-gray-400 dark:border-zinc-500 px-4 py-2">
                              {typeof val === "number" ? val.toFixed(5) : val.toString()}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>

              </Accordion.Body>
            </Accordion.Item>
          );
        }

        // Renderizar os demais como antes
        return (
          <Accordion.Item eventKey={`item-${index}`} key={`item-${index}`}>
            <Accordion.Header>{translateKey(key)}</Accordion.Header>
            <Accordion.Body>
              {typeof value === "object" && value !== null ? (
                Array.isArray(value) ? (
                  value.map((item, subIndex) => (
                    <div key={subIndex} className="border p-2 rounded mb-2">
                      {typeof item === "object" && item !== null ? (
                        <RecursiveAccordion data={item} />
                      ) : (
                        item.toString()
                      )}
                    </div>
                  ))
                ) : (
                  <RecursiveAccordion data={value} />
                )
              ) : (
                value.toString()
              )}
            </Accordion.Body>
          </Accordion.Item>
        );
      })}
    </Accordion>
  );
}
