import { useEffect, useState } from "react";
import { useForm, useFieldArray } from "react-hook-form";
import { Input } from "../../../components/ui/input";
import { Textarea } from "../../../components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger } from "../../../components/ui/select";
import { Button } from "../../../components/ui/button";
import { Plus } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function ExerciseForm({ defaultValues = {}, onSubmit, onCancel, isEdit = false }) {
  const navigate = useNavigate();

  // console.log("Default Values:", defaultValues);

  const {
    register,
    handleSubmit,
    control,
    formState: { errors, isSubmitting },
    setValue,
  } = useForm({
    defaultValues: {
      title: defaultValues.title || "",
      category: defaultValues.category || "",
      objective: defaultValues.objective || "",
      description: defaultValues.description || "",
      duration: defaultValues.duration || "",
      repetitions: defaultValues.repetitions || "",
      difficulty: defaultValues.difficulty || "",
      feedback: defaultValues.feedback || "",
      notes: defaultValues.notes || "",
      steps: defaultValues.steps || [{ instruction: "" }],
    },
  });

  const { fields, append } = useFieldArray({
    control,
    name: "steps",
  });

  // ✅ Estados para mídias
  const [images, setImages] = useState([]);
  const [videos, setVideos] = useState([]);
  const [audios, setAudios] = useState([]);

  // ✅ Inicializa mídias se for modo edição
  useEffect(() => {
    if (isEdit && defaultValues.media) {
      const imgs = defaultValues.media.filter((m) => m.type === "image").map((m) => ({ url: m.url, existing: true }));
      const vids = defaultValues.media.filter((m) => m.type === "video").map((m) => ({ url: m.url, existing: true }));
      const auds = defaultValues.media.filter((m) => m.type === "audio").map((m) => ({ url: m.url, existing: true }));
      setImages(imgs);
      setVideos(vids);
      setAudios(auds);
    }
  }, [defaultValues, isEdit]);

  // ✅ Upload e preview de arquivos novos
  const handleFileChange = (e, type) => {
    const files = Array.from(e.target.files);
    const previews = files.map((file) => ({
      file,
      preview: URL.createObjectURL(file),
    }));

    if (type === "images") setImages((prev) => [...prev, ...previews]);
    if (type === "videos") setVideos((prev) => [...prev, ...previews]);
    if (type === "audios") setAudios((prev) => [...prev, ...previews]);
  };

  // ✅ Remover arquivo (novo ou existente)
  const removeFile = (type, index) => {
    if (type === "images") setImages((prev) => prev.filter((_, i) => i !== index));
    if (type === "videos") setVideos((prev) => prev.filter((_, i) => i !== index));
    if (type === "audios") setAudios((prev) => prev.filter((_, i) => i !== index));
  };

  // ✅ Submissão
  const onSubmitHandler = async (data) => {
    const formData = new FormData();

    Object.keys(data).forEach((key) => {
      if (key !== "steps") formData.append(key, data[key]);
    });

    // Passos (como JSON)
    formData.append("steps", JSON.stringify(data.steps));

    // Mídias novas
    images.forEach((img) => {
      if (img.file) formData.append("images", img.file);
    });
    videos.forEach((vid) => {
      if (vid.file) formData.append("videos", vid.file);
    });
    audios.forEach((aud) => {
      if (aud.file) formData.append("audios", aud.file);
    });

    // Mídias existentes (para não perder as antigas)
    const existingMedia = [
      ...images.filter((m) => m.existing).map((m) => ({ type: "image", url: m.url })),
      ...videos.filter((m) => m.existing).map((m) => ({ type: "video", url: m.url })),
      ...audios.filter((m) => m.existing).map((m) => ({ type: "audio", url: m.url })),
    ];
    formData.append("existingMedia", JSON.stringify(existingMedia));

    await onSubmit(formData);
  };

  return (
    <div className="min-h-screen flex items-center bg-gray-100 dark:bg-zinc-900 px-4">
    <form onSubmit={handleSubmit(onSubmitHandler)} className="space-y-4 max-w-3xl mx-auto">
      <Input placeholder="Título do exercício" {...register("title", { required: "Título é obrigatório" })} />
      {errors.title && <p className="text-red-500 text-sm">{errors.title.message}</p>}

      {/* Categoria */}
      <Select {...register("category")}>
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
      </Select>

      <Textarea placeholder="Objetivo terapêutico" {...register("objective")} />
      <Textarea placeholder="Descrição / instruções" {...register("description")} />

      {/* --- MÍDIAS --- */}
      <div className="space-y-6 mt-6">
        {/* Imagens */}
        <div>
          <label className="block font-semibold">Imagens</label>
          <Input type="file" accept="image/*" multiple onChange={(e) => handleFileChange(e, "images")} />
          <div className="flex flex-wrap gap-3 mt-3">
            {images.map((img, i) => (
              <div key={i} className="relative">
                <img
                  src={img.preview || img.url}
                  alt="preview"
                  className="w-24 h-24 object-cover rounded-lg border"
                />
                <button
                  type="button"
                  onClick={() => removeFile("images", i)}
                  className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Vídeos */}
        <div>
          <label className="block font-semibold">Vídeos</label>
          <Input type="file" accept="video/*" multiple onChange={(e) => handleFileChange(e, "videos")} />
          <div className="flex flex-wrap gap-3 mt-3">
            {videos.map((vid, i) => (
              <div key={i} className="relative">
                <video
                  src={vid.preview || vid.url}
                  controls
                  className="w-40 h-28 rounded-lg border"
                />
                <button
                  type="button"
                  onClick={() => removeFile("videos", i)}
                  className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Áudios */}
        <div>
          <label className="block font-semibold">Áudios</label>
          <Input type="file" accept="audio/*" multiple onChange={(e) => handleFileChange(e, "audios")} />
          <div className="flex flex-col gap-2 mt-2">
            {audios.map((aud, i) => (
              <div key={i} className="flex items-center gap-2 relative">
                <audio controls src={aud.preview || aud.url} className="w-64" />
                <button
                  type="button"
                  onClick={() => removeFile("audios", i)}
                  className="bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* --- PASSOS --- */}
      <div>
        <h3 className="text-lg font-semibold mb-2">Passos</h3>
        {fields.map((field, index) => (
          <div key={field.id} className="mb-2 border p-2 rounded-lg">
            <Input placeholder={`Instrução do passo ${index + 1}`} {...register(`steps.${index}.instruction`)} />
            {errors.steps?.[index]?.instruction && (
              <p className="text-red-500 text-sm">{errors.steps[index].instruction.message}</p>
            )}
          </div>
        ))}
        <Button type="button" onClick={() => append({ instruction: "" })} variant="outline" className="mt-2 rounded">
          <Plus className="w-4 h-4 mr-1" /> Adicionar Passo
        </Button>
      </div>

      {/* --- DURAÇÃO / REPETIÇÕES / DIFICULDADE --- */}
      <div className="grid grid-cols-2 gap-4">
        <Input type="number" placeholder="Duração (min)" {...register("duration")} />
        <Input type="number" placeholder="Repetições" {...register("repetitions")} />
      </div>

      <Select {...register("difficulty")}>
        <SelectTrigger>Dificuldade</SelectTrigger>
        <SelectContent>
          <SelectItem value="Iniciante">Iniciante</SelectItem>
          <SelectItem value="Intermédio">Intermédio</SelectItem>
          <SelectItem value="Avançado">Avançado</SelectItem>
        </SelectContent>
      </Select>

      <Textarea placeholder="Feedback esperado" {...register("feedback")} />
      <Textarea placeholder="Notas do terapeuta" {...register("notes")} />

      {/* --- BOTÕES --- */}
      <div className="flex flex-col gap-3 mt-6">
        <Button type="submit" className="w-full bg-green-500 rounded" disabled={isSubmitting}>
          {isSubmitting ? "Salvando..." : isEdit ? "Salvar Alterações" : "Criar Exercício"}
        </Button>
        <Button
          type="button"
          variant="outline"
          className="w-full rounded bg-blue-600 text-white"
          onClick={onCancel || (() => navigate(-1))}
        >
          Cancelar
        </Button>
      </div>
    </form>
    </div>
  );
}
