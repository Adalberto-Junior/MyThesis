import React from "react";
import { useForm } from "react-hook-form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";

export default function RelatorioAnaliseForm({ utenteId, terapeutaId, onSave }) {
  const { register, handleSubmit, reset } = useForm();

  const onSubmit = async (data) => {
    const payload = {
      ...data,
      utente_id: utenteId,
      terapeuta_id: terapeutaId,
      status: "finalizado",
      views: 0,
      created_at: new Date().toISOString(),
    };

    const response = await fetch("/api/relatorios", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (response.ok) {
      const result = await response.json();
      onSave?.(result);
      reset();
      alert("Relatório salvo com sucesso!");
    } else {
      alert("Erro ao salvar relatório.");
    }
  };

  return (
    <div className="max-w-2xl mx-auto bg-white dark:bg-zinc-800 p-6 rounded-xl shadow">
      <h2 className="text-xl font-semibold mb-4">Escrever Relatório da Análise</h2>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <Input
          label="Título do Relatório"
          placeholder="Ex: Análise de Fonação - 10/06/2025"
          {...register("title", { required: true })}
        />

        <Select label="Tipo de Análise" {...register("type", { required: true })}>
          <option value="articulation">Articulação</option>
          <option value="fonation">Fonação</option>
          <option value="prosody">Prosódia</option>
          <option value="glottis">Glota</option>
        </Select>

        <Input
          type="date"
          label="Data da Análise"
          {...register("analysis_date", { required: true })}
        />

        <Textarea
          label="Observações Principais"
          placeholder="Descreva os principais achados da análise..."
          rows={4}
          {...register("observations")}
        />

        <Textarea
          label="Recomendações ao Paciente"
          placeholder="Sugira exercícios ou hábitos para a próxima semana..."
          rows={3}
          {...register("recommendations")}
        />

        <Textarea
          label="Nota Confidencial (opcional)"
          placeholder="Visível apenas para o terapeuta."
          rows={2}
          {...register("internal_note")}
        />
        <Select
          label="Status do Relatório"
          {...register("status", { required: true })}
        >
          <option value="rascunho">Rascunho</option>
          <option value="finalizado">Finalizado</option>
        </Select>

        <Button type="submit" className="bg-blue-600 text-white hover:bg-blue-700">
          Salvar Relatório
        </Button>
      </form>
    </div>
  );
} 
// This code defines a form for creating a report related to a patient's analysis, including fields for title, type, date, observations, recommendations, and an internal note. It uses React Hook Form for form handling and includes basic validation. The form submits data to an API endpoint and provides feedback on success or failure.
// The form is styled with Tailwind CSS classes for a clean and modern look, ensuring a user-friendly experience. The `onSubmit` function handles the form submission, sending the data to the server and resetting the form upon success. The component is designed to be reusable, allowing it to be integrated into different parts of a healthcare application where patient analysis reports are needed.