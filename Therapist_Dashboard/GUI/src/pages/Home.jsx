
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Accordion from "react-bootstrap/Accordion";
import api from "../api";



export default function Home() {
  const [notas, setNotas] = useState([]);
  const [novaNota, setNovaNota] = useState('');
  const [prioridade, setPrioridade] = useState('média');
  const [categoria, setCategoria] = useState('Trabalho');
  const [dataExecucao, setDataExecucao] = useState('');
  const [modoOrdenacao, setModoOrdenacao] = useState('data');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchNotas() {
      try {
        const res = await api.get('/auth/notas');
        setNotas(Array.isArray(res.data) ? res.data : []);
      } catch (error) {
        setError(error);
      } finally {
        setLoading(false);
      }
    }
    fetchNotas();
  }, []);

  const handleAdicionarNota = async () => {
    if (!novaNota.trim()) return;
    const nova = {
      texto: novaNota,
      prioridade,
      categoria,
      dataExecucao,
      done: false,
      data: new Date().toISOString(),
    };
    await api.post('/auth/notas', nova);
    window.location.reload();
  };

  const handleToggleDone = async (nota) => {
    if (!nota || !nota._id) return;
    if (typeof nota._id === 'object' && nota._id.$oid) {
      nota._id = nota._id.$oid; // converte se necessário
    }
    const atualizada = { ...nota, done: !nota.done };
    console.log(atualizada);
    if (typeof atualizada._id === 'object' && atualizada._id.$oid) {
      atualizada._id = atualizada._id.$oid; // converte se necessário
    }
    if (typeof atualizada.therapist === 'object' && atualizada.therapist.$oid) {
      atualizada.therapist = atualizada.therapist.$oid; // converte se necessário
    }
    await api.put(`/auth/notas/${nota._id}`, atualizada); // assume rota RESTful
    setNotas(notas.map(n => (n._id === nota._id ? atualizada : n)));
  };

  const handleDeleteNota = async (notaId) => {
    if (!notaId) return;
    
    if (!window.confirm('Tem certeza que deseja excluir esta nota?')) return;

    if (typeof notaId === 'object' && notaId.$oid) {
      notaId = notaId.$oid;
    }
    await api.delete(`/auth/notas/${notaId}`);
    setNotas(notas.filter(n => n._id !== notaId));
    window.location.reload();

  };
  // Ordena as notas por prioridade ou data
  const notasOrdenadas = [...notas].sort((a, b) => {
    if (modoOrdenacao === 'priority') {
      const ordem = { alta: 0, média: 1, baixa: 2 };
      return ordem[a.priority] - ordem[b.priority];
    }
    return new Date(b.date) - new Date(a.date);
  });

  const tarefasAtivas = notasOrdenadas.filter(n => !n.done);
  const tarefasFeitas = notasOrdenadas.filter(n => n.done);

  if (loading){
        return(
         <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-zinc-900 px-4">
            <p className="text-2xl font-semibold text-center  dark:text-white mb-6">Loading...</p>
        </div>
        );
    }
  if (error) {
        return (
          <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-zinc-900 px-4">
              <p className="text-2xl font-semibold text-center dark:text-white mb-6">Error: {error.message}</p>
          </div>
        ) 
  }


  return (
        <>
          <div className="min-h-screen bg-gray-100 dark:bg-zinc-900 text-black dark:text-white p-6">
            <div className="container mx-auto max-w-4xl mt-10 p-5 bg-white dark:bg-zinc-800 rounded-lg shadow-md">
              <div className="mb-6">
                <h2 className="text-2xl font-semibold mb-4">Nova Tarefa</h2>
                <div className="space-y-4">
                  <textarea
                    className="w-full p-2 px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-zinc-700 dark:border-zinc-600 dark:text-white"
                    rows="2"
                    placeholder="Escreva a tarefa..."
                    value={novaNota}
                    onChange={(e) => setNovaNota(e.target.value)}
                  />
                  <div className="flex gap-2 flex-wrap">
                    <select value={prioridade} onChange={(e) => setPrioridade(e.target.value)} className="rounded px-2 py-1 dark:bg-zinc-700">
                      <option value="alta">Alta</option>
                      <option value="média">Média</option>
                      <option value="baixa">Baixa</option>
                    </select>
                    <select value={categoria} onChange={(e) => setCategoria(e.target.value)} className="rounded px-2 py-1 dark:bg-zinc-700">
                      <option>Trabalho</option>
                      <option>Reunião</option>
                      <option>Consulta</option>
                      <option>Estudo</option>
                      <option>Outro</option>
                    </select>
                    <input
                      type="date"
                      value={dataExecucao}
                      onChange={(e) => setDataExecucao(e.target.value)}
                      className="rounded px-2 py-1 dark:bg-zinc-700"
                    />
                    <button onClick={handleAdicionarNota} className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                      Adicionar
                    </button>
                  </div>
                </div>
              </div>

              <div className="mb-6">
                <div className="flex justify-end mb-2">
                  <label className="mr-2">Ordenar por:</label>
                  <select value={modoOrdenacao} onChange={(e) => setModoOrdenacao(e.target.value)} className="rounded px-2 py-1 dark:bg-zinc-700">
                    <option value="date">Data</option>
                    <option value="priority">Prioridade</option>
                  </select>
                </div>

                <h2 className="text-xl font-semibold mb-2">Tarefas Pendentes</h2>
                {tarefasAtivas.length > 0 ? (
                  <ul className="space-y-4">
                    {tarefasAtivas.map(nota => (
                      <li key={nota._id} className={`border-l-4 p-4 rounded shadow-md dark:bg-zinc-700 ${
                        nota.priority === 'alta'
                          ? 'border-red-500'
                          : nota.priority === 'média'
                          ? 'border-yellow-500'
                          : 'border-green-500'
                      }`}>
                        <div className="flex justify-between items-center">
                          <span className="font-semibold capitalize text-gray-500 dark:text-gray-300">
                            Prioridade: {nota.priority}
                          </span>
                          <input
                            type="checkbox"
                            checked={nota.done}
                            onChange={() => handleToggleDone(nota)}
                            className="w-5 h-5"
                          />
                        </div>

                        <div className="text-sm text-gray-500 dark:text-gray-300">
                          {nota.dataExecucao
                            ? `Para: ${new Date(nota.dataExecucao).toLocaleDateString()}`
                            : 'Sem data'} | Categoria: {nota.category || 'Não definida'}
                        </div>
                        <p className="mt-2 whitespace-pre-line">{nota.note || nota.texto}</p>
                        <button
                          onClick={() => handleDeleteNota(nota._id)}
                          className="text-red-500 hover:underline mt-2"
                        >
                          Excluir
                        </button>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <div className="text-center text-gray-500 dark:text-gray-400 italic mt-4">
                    🎉 Nenhuma tarefa pendente no momento!
                  </div>
                )}

              </div>

              <div className="mt-8 p-1">
                {/* <h2 className="text-xl font-semibold mt-8 mb-2">Tarefas Concluídas</h2> */}
                <Accordion defaultActiveKey="0" className="mb-6">
                  <Accordion.Item eventKey="0">
                    <Accordion.Header>Tarefas Concluídas</Accordion.Header>
                    <Accordion.Body>
                      <ul className="space-y-4">
                        {tarefasFeitas.map(nota => (
                          <li key={nota._id} className={`border-l-4 p-4 rounded shadow-md dark:bg-zinc-700 ${nota.priority === 'alta' ? 'border-red-500' : nota.priority === 'média' ? 'border-yellow-500' : 'border-green-500'}`}>
                            <div className="flex justify-between items-center">
                              <span className="font-semibold capitalize  text-gray-500 dark:text-gray-300">Prioridade: {nota.priority}</span>
                              <input
                                type="checkbox"
                                checked={nota.done}
                                onChange={() => handleToggleDone(nota)}
                                className="w-5 h-5"
                              />
                            </div>
                            <div className="text-sm text-gray-500 dark:text-gray-300">
                              {nota.dataExecucao ? `Para: ${new Date(nota.dataExecucao).toLocaleDateString()}` : 'Sem data'} | Categoria: {nota.category || 'Não definida'}
                            </div>
                            <p className="mt-2 whitespace-pre-line dark:text-white">{nota.note || nota.texto}</p>
                            <button onClick={() => handleDeleteNota(nota._id)} className="text-red-500 hover:underline mt-2">
                              Excluir
                            </button>
                          </li>
                        ))}
                      </ul>
                    </Accordion.Body>
                  </Accordion.Item>
                </Accordion>
              </div>
            </div>
          </div>
        </>
  )
}