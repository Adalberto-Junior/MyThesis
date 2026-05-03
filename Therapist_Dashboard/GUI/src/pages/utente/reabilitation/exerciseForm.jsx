
import { useState } from "react";
import { useForm, useFieldArray, Controller } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { Card, CardHeader, CardTitle, CardContent } from "../../../components/ui/card"
import { Input } from "../../../components/ui/input";
import { Textarea } from "../../../components/ui/textarea";
import { Select, SelectTrigger,SelectValue, SelectContent, SelectItem } from "../../../components/ui/select";
import { Button } from "../../../components/ui/button";
import { X, Plus, Minus } from "lucide-react";
import api from "../../../api";
import { useParams, useNavigate } from "react-router-dom";

const schema = z.object({
  title: z.string().min(1, "Título é obrigatório"),
  category: z.string(),
  objective: z.string().optional(),
  description: z.string().optional(),
  duration: z.string().optional(),
  repetitions: z.string().optional(),
  difficulty: z.string(),
  feedback: z.string().optional(),
  notes: z.string().optional(),
  steps: z.array(
    z.object({
      instruction: z.string().min(1, "Instrução obrigatória"),
    })
  ),
});

export default function ExerciseForm() {
  const [images, setImages] = useState([]);
  const [videos, setVideos] = useState([]);
  const [audios, setAudios] = useState([]);
  const { id } = useParams();
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    control,
    reset,
    formState: { errors, isSubmitting },
  } = useForm({
    resolver: zodResolver(schema),
    defaultValues: {
      title: "",
      category: "Articulação",
      objective: "",
      description: "",
      duration: "",
      repetitions: "",
      difficulty: "Iniciante",
      feedback: "",
      notes: "",
      steps: [{ instruction: "" }],
    },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: "steps",
  });

  // Upload de ficheiros
  const handleFileChange = (e, type) => {
    const files = Array.from(e.target.files).map((file) => ({
      file,
      preview: URL.createObjectURL(file),
    }));

    if (type === "images") setImages((prev) => [...prev, ...files]);
    if (type === "videos") setVideos((prev) => [...prev, ...files]);
    if (type === "audios") setAudios((prev) => [...prev, ...files]);
  };

  const removeFile = (type, index) => {
    if (type === "images") setImages(images.filter((_, i) => i !== index));
    if (type === "videos") setVideos(videos.filter((_, i) => i !== index));
    if (type === "audios") setAudios(audios.filter((_, i) => i !== index));
  };

  const onSubmit = async (data) => {
    const formData = new FormData();
    // console.log("Dados do formulário:", data);

    Object.keys(data).forEach((key) => {
      if (key === "steps") {
        formData.append("steps", JSON.stringify(data.steps));
      } else {
        formData.append(key, data[key]);
      }
    });

    images.forEach(({ file }) => formData.append("images", file));
    videos.forEach(({ file }) => formData.append("videos", file));
    audios.forEach(({ file }) => formData.append("audios", file));

    // console.log("FormData preparado para envio:", [...formData.entries()]); // para ver conteúdo

    try {
      const response = await api.post(
        `/utente/rehabilitation/${id}/exercises/`,
        formData
        // 👇 NÃO definir manualmente Content-Type!
      );

      if (response.status === 200 || response.status === 201) {
        alert("Exercício salvo com sucesso!");
        reset();
        setImages([]);
        setVideos([]);
        setAudios([]);
      } else {
        alert("Erro ao salvar exercício");
      }
    } catch (err) {
      console.error(err);
      alert("Erro na conexão com o servidor");
    }
  };


  return (
    <div className="min-h-screen flex items-center bg-gray-100 dark:bg-zinc-900 px-4">
      <Card className="w-200 mx-auto shadow-lg my-8 rounded-2xl">
        <CardHeader>
          <CardTitle className="text-2xl font-bold">Adicionar Exercício</CardTitle>
        </CardHeader>
        <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 ">
          <Input
            placeholder="Título do exercício"
            {...register("title")}
            className="w-full mb-4"
          />
          {errors.title && <p className="text-red-500 text-sm">{errors.title.message}</p>}

          {/* <Select {...register("category")}
            className="mb-2"
          >
            <SelectTrigger>Categoria</SelectTrigger>
            <SelectContent>
              <SelectItem value="Articulação">Articulação</SelectItem>
              <SelectItem value="Fonação">Fonação</SelectItem>
              <SelectItem value="Prosódia">Prosódia</SelectItem>
              <SelectItem value="Orofaciais">Orofaciais</SelectItem>
              <SelectItem value="Linguagem e Cognição">Linguagem e Cognição</SelectItem>
              <SelectItem value="Fluência">Fluência</SelectItem>
              <SelectItem value="Reaprendizagem">Reaprendizagem</SelectItem>
            </SelectContent>
            
          </Select> */}

          <Controller
            name="category"
            control={control}
            render={({ field }) => (
              <Select value={field.value} onValueChange={field.onChange} className="mb-2">
                <SelectTrigger>
                  <SelectValue placeholder="Categoria" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Articulação">Articulação</SelectItem>
                  <SelectItem value="Fonação">Fonação</SelectItem>
                  <SelectItem value="Prosódia">Prosódia</SelectItem>
                  <SelectItem value="Orofaciais">Orofaciais</SelectItem>
                  <SelectItem value="Linguagem e Cognição">Linguagem e Cognição</SelectItem>
                  <SelectItem value="Fluência">Fluência</SelectItem>
                  <SelectItem value="Reaprendizagem">Reaprendizagem</SelectItem>
                </SelectContent>
              </Select>
            )}
          />

          <div className="flex gap-4"></div>

          <Textarea placeholder="Objetivo terapêutico" {...register("objective")} className="w-full mb-3" />
          <Textarea placeholder="Descrição / instruções" {...register("description")} className="w-full mb-3" />

          {/* Uploads */}
          <div className="space-y-4">
            <div>
              <label className="block font-semibold">Imagens</label>
              <Input type="file" accept="image/*" multiple onChange={(e) => handleFileChange(e, "images")} />
              <div className="flex flex-wrap gap-2 mt-2">
                {images.map((img, i) => (
                  <div key={i} className="relative">
                    <img src={img.preview} alt="preview" className="w-24 h-24 object-cover rounded-lg border" />
                    <button
                      type="button"
                      onClick={() => removeFile("images", i)}
                      className="absolute top-26 right bg-red-500 text-white rounded w-0 h-6 flex items-center justify-center"
                    >
                      Apagar
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div>
          <label className="block font-semibold">Vídeos</label>
           <Input
             type="file"
             accept="video/*"
             multiple
             onChange={(e) => handleFileChange(e, "videos")}
           />
           <div className="flex flex-wrap gap-2 mt-2">
             {videos.map((vid, index) => (
               <div key={index} className="relative">
                 <video
                   src={vid.preview}
                   controls
                 className="w-40 h-28 rounded-lg border"
                />
                 <button
                   type="button"
                   onClick={() => removeFile("videos", index)}
                   className="absolute top right bg-red-500 text-white rounded-full w-6 h-6"
                 >
                   cancelar
                 </button>
               </div>
             ))}
           </div>
         </div>

        <div>
          <label className="block font-semibold">Áudios</label>
          <Input
            type="file"
            accept="audio/*"
            multiple
            onChange={(e) => handleFileChange(e, "audios")}
          />
          <div className="flex flex-col gap-2 mt-2">
            {audios.map((aud, index) => (
              <div key={index} className="flex items-center gap-2 relative">
                <audio controls src={aud.preview} className="w-64" />
                <button
                  type="button"
                  onClick={() => removeFile("audios", index)}
                  className="bg-red-500 text-white rounded w-2 h-9"
                >
                  cancelar
                </button>
              </div>
            ))}
          </div>
        </div>

          {/* Passos */}
          <div>
            <h3 className="text-lg font-semibold mb-2">Passos</h3>
            {fields.map((field, index) => (
              <div key={field.id} className="mb-2 border p-2 rounded-lg">
                <Input
                  placeholder={`Instrução do passo ${index + 1}`}
                  {...register(`steps.${index}.instruction`)}
                />
                {errors.steps?.[index]?.instruction && (
                  <p className="text-red-500 text-sm">{errors.steps[index].instruction.message}</p>
                )}
                <Button
                  type="button"
                  variant="outline"
                  className="mt-2 rounded bg-red-500"
                  onClick={() => remove(field.id)}
                >
                  <Minus className="w-4 h-4 mr-1" /> Remover Passo
                </Button>

              </div>
            ))}
            <Button type="button" onClick={() => append({ instruction: "" })} variant="outline" className="mt-2 rounded bg-green-400">
              <Plus className="w-4 h-4 mr-1" /> Adicionar Passo
            </Button>
            

          </div>

          <div className="grid grid-cols-2 gap-4">
            <Input type="number" placeholder="Duração (min)" {...register("duration")} />
            <Input type="number" placeholder="Repetições" {...register("repetitions")} />
          </div>

          {/* <Select {...register("difficulty")}>
            <SelectTrigger>Dificuldade</SelectTrigger>
            <SelectContent>
              <SelectItem value="Iniciante">Iniciante</SelectItem>
              <SelectItem value="Intermédio">Intermédio</SelectItem>
              <SelectItem value="Avançado">Avançado</SelectItem>
            </SelectContent>
          </Select> */}
          <Controller
            name="difficulty"
            control={control}
            render={({ field }) => (
              <Select value={field.value} onValueChange={field.onChange} className="mb-2">
                <SelectTrigger>
                  <SelectValue placeholder="Dificuldade" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Iniciante">Iniciante</SelectItem>
                  <SelectItem value="Intermédio">Intermédio</SelectItem>
                  <SelectItem value="Avançado">Avançado</SelectItem>
                </SelectContent>
              </Select>
            )}
          />
          <div className="flex gap-4"></div>
          <span
            className="text-gray-400 cursor-pointer"
            title="O que o terapeuta espera como resultado do utente. Ex: 'Pronunciar a palavra sem omissões', 'Sustentar a vogal por 5s'."
          >
            ℹ️
          </span>
          <Textarea placeholder="Feedback esperado"  {...register("feedback")} className="w-full mb-3" />
          <Textarea placeholder="Notas do terapeuta" {...register("notes")} className="w-full mb-3" />

          <Button type="submit" className="w-full rounded bg-green-500" disabled={isSubmitting}>
            {isSubmitting ? "Salvando..." : "Salvar Exercício"}
          </Button>
          <div className="flex gap-4"></div>
          <Button type="button" variant="outline" className="w-full rounded bg-blue-600" onClick={() => navigate(-1)}>
            Fechar
          </Button>
        </form>
      </CardContent>
    </Card>
    </div>
  );
}
