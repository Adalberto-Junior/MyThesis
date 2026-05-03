
import React, { useEffect, useState } from "react";
import api from "../../../api";
import { useNavigate, useParams } from "react-router-dom";
import FloatingForm from "./floatingUtenteForm";
import { Card, CardHeader, CardTitle, CardContent } from "../../../components/ui/card";
import { Button } from "../../../components/ui/button";
import { Loader2, UserPlus, Eye } from "lucide-react";

export default function AllUtente() {
  const [utentes, setUtentes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const { id } = useParams();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get("/utente/");
        setUtentes(response.data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleOpen = (id) => {
    navigate(`/utente/${id}/informacao`);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 dark:bg-zinc-900 px-4">
        <Loader2 className="h-10 w-10 animate-spin text-primary mb-4" />
        <p className="text-lg font-semibold dark:text-white">Carregando utentes...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-zinc-900 px-4">
        <p className="text-lg font-semibold text-red-600 dark:text-red-400">
          Erro ao carregar utentes: {error.message}
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold dark:text-white">Lista de Utentes</h2>
        <Button onClick={() => setShowForm(true)} className="flex items-center gap-2 rounded">
          <UserPlus size={18} /> Adicionar Utente
        </Button>
      </div>

      {utentes.length === 0 ? (
        <Card>
          <CardContent className="p-6 text-center">
            <p className="text-lg font-semibold dark:text-white mb-4">Nenhum utente encontrado.</p>
            <Button onClick={() => setShowForm(true)} className="flex items-center gap-2">
              <UserPlus size={18} /> Criar Primeiro Utente
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-gray-100 dark:bg-zinc-800 text-gray-700 dark:text-gray-300">
                    <th className="p-3 font-semibold">ID</th>
                    <th className="p-3 font-semibold">Nome</th>
                    <th className="p-3 font-semibold">Email</th>
                    <th className="p-3 font-semibold text-center">Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {utentes.map((utente) => {
                    const utenteId = utente._id?.$oid || utente._id?.toString();
                    return (
                      <tr
                        key={utenteId}
                        className="hover:bg-gray-50 dark:hover:bg-zinc-700 transition-colors"
                      >
                        <td className="p-3 text-sm text-gray-600 dark:text-gray-300">{utenteId}</td>
                        <td className="p-3 font-medium dark:text-white">{utente.name}</td>
                        <td className="p-3 text-gray-600 dark:text-gray-300">{utente.email}</td>
                        <td className="p-3 text-center">
                          <Button
                            onClick={() => handleOpen(utenteId)}
                            variant="outline"
                            size="sm"
                            className="flex items-center gap-1 rounded"
                          >
                            <Eye size={16} /> Abrir
                          </Button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {showForm && <FloatingForm onClose={() => setShowForm(false)} />}
    </div>
  );
}
