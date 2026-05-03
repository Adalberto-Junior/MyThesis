import React, { useEffect, useState, useCallback, useMemo } from "react";
import { useParams } from "react-router-dom";
import { useForm, useFieldArray, Controller } from "react-hook-form";
import { ErrorMessage } from "@hookform/error-message";
import api from "../../../api";
import { StepFields } from "./StepFields";
import { ExerciseMetaFields } from "./ExerciseMetaFields";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "../../../components/ui/dialog";
import { Input } from "../../../components/ui/input";
import { Textarea } from "../../../components/ui/textarea";
import { Button } from "../../../components/ui/button";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "../../../components/ui/select";
import { Loader2, XCircle, PlusCircle } from "lucide-react";
import { MultiSelect } from "primereact/multiselect";

function ExerciseSteps({
  type,
  fields,
  camposPorTipo,
  camposPorTipoEn,
  editable,
  register,
  remove,
  appendStep,
}) {
  if (!fields || fields.length === 0) return null;

  return (
    <div className="rounded-xl border p-4 bg-muted/30">
      <h3 className="text-lg font-semibold mb-2">
        Passos <span className="text-red-500">*</span>
      </h3>
      {fields.map((field, index) => (
        <div key={field.id || index} className="mb-4">
          <StepFields
            index={index}
            type={type}
            field={field}
            camposPorTipo={camposPorTipo}
            camposPorTipoEn={camposPorTipoEn}
            editable={editable}
            register={register}
            remove={remove}
          />
        </div>
      ))}
      {editable && (
        <Button
          type="button"
          variant="outline"
          onClick={appendStep}
          className="mt-2 flex items-center gap-2"
        >
          <PlusCircle size={16} /> Adicionar passo
        </Button>
      )}
    </div>
  );
}

function ExerciseSelectedDetails({
  dadosExercicioSelecionado,
  modoEdicao,
  setDadosExercicioSelecionado,
  control,
  options,
  errors,
  type,
  camposPorTipo,
  camposPorTipoEn,
  register,
  remove,
  appendStep,
  fields,
}) {
  if (!dadosExercicioSelecionado) return null;

  return (
    <div className="rounded-xl border p-4 bg-muted/30">
      <div className="space-y-3">
        <div>
          <label className="font-semibold">
            Nome <span className="text-red-500">*</span>
          </label>
          <Input
            {...register("name")}
            readOnly={modoEdicao === "default"}
            defaultValue={dadosExercicioSelecionado.name || ""}
            onChange={(e) =>
              modoEdicao === "personalizar" &&
              setDadosExercicioSelecionado((prev) => ({
                ...prev,
                name: e.target.value,
              }))
            }
          />
        </div>

        <div>
          <label className="font-semibold">Descrição</label>
          <Textarea
            {...register("description")}
            readOnly={modoEdicao === "default"}
            defaultValue={dadosExercicioSelecionado.description || ""}
            onChange={(e) =>
              modoEdicao === "personalizar" &&
              setDadosExercicioSelecionado((prev) => ({
                ...prev,
                description: e.target.value,
              }))
            }
          />
        </div>

        <div>
          <label className="font-semibold">
            Tipo de Processamento <span className="text-red-500">*</span>
          </label>
            {/* <Controller
              name="typeOfProcessing"
              control={control}
              rules={{ required: "Selecione pelo menos um tipo." }}
              render={({ field }) => (
                <MultiSelect
                  value={field.value || []}
                  options={options}
                  optionLabel="label"
                  optionValue="value"
                  filter
                  placeholder="Selecione os tipos"
                  display="chip"
                  className="w-full"
                  onChange={(e) => field.onChange(e.value)}
                  onBlur={field.onBlur}
                />
              )}
            /> */}
            {/* <Controller
            name="typeOfProcessing"
            control={control}
            rules={{ required: "Selecione pelo menos um tipo." }}
            render={({ field }) => (
                <MultiSelect
                {...field}
                value={field.value || []}  // ✅ agora controlado pelo RHF
                onChange={(e) => field.onChange(e.value)} // ✅ garante atualização
                options={options}
                optionLabel="label"
                optionValue="value"
                filter
                placeholder="Selecione os tipos de processamento"
                display="chip"
                disabled={modoEdicao === "default"}
                className={`w-full md:w-20rem ${
                    modoEdicao === "default" ? "bg-gray-400" : "bg-gray-800"
                }`}
                />
            )}
        /> */}

        <Controller
          name="typeOfProcessing"
          control={control}
          rules={{
            required: "Selecione pelo menos um tipo de Processamento.",
            validate: (value) => value?.length > 0 || "Selecione pelo menos um tipo.",
          }}
          render={({ field }) => {
            // garante que value é sempre um array de strings
            const value = Array.isArray(field.value) ? field.value : [];

            // opcional: um key que força remount quando o value/options mudam (resolve estados estranhos do overlay)
            const key = `${value.join(",")}-${options.map(o => o.value).join(",")}`;

            return (
              <MultiSelect
                key={key}
                value={value}
                options={options}
                optionLabel="label"
                optionValue="value"
                filter
                placeholder="Selecione os tipos"
                display="chip"
                className="w-full"
                onChange={(e) => field.onChange(e.value)} // usa e.value (array)
                onBlur={field.onBlur}
                appendTo={document.body} // renderiza o painel no body, evita overlays/overflow a bloquear o dropdown
              />
            );
          }}
        />


          <ErrorMessage
            errors={errors}
            name="typeOfProcessing"
            render={({ message }) => (
              <p className="text-red-500 text-sm">{message}</p>
            )}
          />
        </div>

        <ExerciseSteps
          type={type}
          fields={fields}
          camposPorTipo={camposPorTipo}
          camposPorTipoEn={camposPorTipoEn}
          editable={modoEdicao === "personalizar"}
          register={register}
          remove={remove}
          appendStep={appendStep}
        />
      </div>
    </div>
  );
}

export default function FloatingForm({ onClose }) {
  const { id } = useParams();
  const [type, setType] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [exerciciosDisponiveis, setExerciciosDisponiveis] = useState([]);
  const [exercicioSelecionadoId, setExercicioSelecionadoId] = useState("");
  const [dadosExercicioSelecionado, setDadosExercicioSelecionado] = useState(null);
  const [modoEdicao, setModoEdicao] = useState("default");



  // const {
  //   register,
  //   handleSubmit,
  //   watch,
  //   setValue,
  //   control,
  //   reset,
  //   formState: { errors },
  // } = useForm({
  //   defaultValues: {
  //     userId: id,
  //     tipo: "",
  //     steps: [],
  //   },
  // });
    const {
    register,
    handleSubmit,
    watch,
    setValue,
    control,
    reset,
    formState: { errors },
  } = useForm({
    defaultValues: {
      userId: id,
      tipo: "",
      steps: [],
      typeOfProcessing: [],   // <- adiciona isto
      name: "",               // garantir campos vazios por defeito
      description: "",
    },
  });


  const { fields, append, remove, replace } = useFieldArray({ control, name: "steps" });

  const tipoSelecionado = watch("tipo");

  const camposPorTipo = useMemo(
    () => ({
      palavras: ["Palavras", "Instrução", "ID"],
      frases: ["Frase", "Instrução", "ID"],
      leitura: ["Título", "Texto", "Instrução", "ID"],
      discurso: ["Questão", "Instrução", "ID"],
      diadococinesia: ["Tipo de Consoante", "Sílabas", "Instrução", "ID"],
      novo: ["Instrução", "label", "valor", "ID"],
    }),
    []
  );

  const camposPorTipoEn = useMemo(
    () => ({
      palavras: ["word", "description", "ID"],
      frases: ["sentence", "description", "ID"],
      leitura: ["title", "text", "description", "ID"],
      discurso: ["question", "description", "ID"],
      diadococinesia: ["typeOfConsonant", "syllables", "description", "ID"],
      novo: ["description", "label", "value", "ID"],
    }),
    []
  );

  const mapTipo = useCallback(
    (tipo) =>
      ({
        palavras: "Repetição de Palavras",
        frases: "Repetição de Frases",
        leitura: "Atividades de Leitura",
        discurso: "Discurso Espontâneo",
        diadococinesia: "Diadococinésia",
      }[tipo] || tipo),
    []
  );

  const options = useMemo(
    () => [
      { label: "Articulação", value: "articulation" },
      { label: "Fonação", value: "phonation" },
      { label: "Glota", value: "glotta" },
      { label: "Prosódia", value: "prosody" },
      { label: "Reaprendizagem", value: "replearning" },
      { label: "Fonological", value: "phonological" },
    ],
    []
  );

  const appendStep = useCallback(() => {
    const campos = camposPorTipoEn[tipoSelecionado] || [];
    const novoStep = Object.fromEntries(campos.map((key) => [key, ""]));
    append(novoStep);
  }, [tipoSelecionado, append, camposPorTipoEn]);

  // const appendStep = useCallback(() => {
  //   const campos = camposPorTipoEn[tipoSelecionado] || [];
  //   const novoStep = Object.fromEntries(campos.map((key) => [key, ""]));
  //   append(novoStep);
  // }, [tipoSelecionado, append, camposPorTipoEn]);

  const onSubmit = async (data) => {
    try {
      await api.post(`/utente/${id}/exercicio/`, data);
      alert("Exercício adicionado com sucesso!");
      window.location.reload();
    } catch (error) {
      alert(
        `Erro ao adicionar exercício: ${error.response?.data?.error || ""}`
      );
    }
  };

  // Carregar exercícios disponíveis ao selecionar tipo
  useEffect(() => {
    const fetchData = async () => {
      try {
        if (tipoSelecionado) {
          const tipo = mapTipo(tipoSelecionado);
          const response = await api.get(`/utente/exercicios/tipo/${tipo}/`);
          setExerciciosDisponiveis(response.data);
        }
      } catch (error) {
        setError(error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [tipoSelecionado]);

  // Quando o usuário seleciona um exercício, carrega no formulário
  // useEffect(() => {
  //   if (exercicioSelecionadoId) {
  //     const exSelecionado = exerciciosDisponiveis.find(
  //       (ex) => ex._id?.toString() === exercicioSelecionadoId
  //     );
  //     if (exSelecionado) {
  //       setDadosExercicioSelecionado(exSelecionado);
  //       setType(tipoSelecionado); // garante que appendStep usa o tipo correto
  //       reset({
  //         ...exSelecionado,
  //         userId: id,
  //         tipo: tipoSelecionado,
  //         steps: exSelecionado.steps || [],
  //       });
  //     }
  //   } else {
  //     setDadosExercicioSelecionado(null);
  //     reset({
  //       userId: id,
  //       tipo: tipoSelecionado,
  //       steps: [],
  //     });
  //   }
  // }, [exercicioSelecionadoId, exerciciosDisponiveis, reset, id, tipoSelecionado]);

  useEffect(() => {
    // se não há tipo escolhido, não fazemos nada
    if (!tipoSelecionado) return;

    // quando limpam a selecção
    if (!exercicioSelecionadoId) {
      setDadosExercicioSelecionado(null);
      // limpa form e steps
      if (typeof replace === "function") {
        replace([]);
        setValue("name", "");
        setValue("description", "");
        setValue("typeOfProcessing", []);
        setValue("tipo", tipoSelecionado);
      } else {
        reset({ userId: id, tipo: tipoSelecionado, name: "", description: "", typeOfProcessing: [], steps: [] });
      }
      return;
    }

    // tenta encontrar por _id (string), por _id.$oid (algumas APIs devolvem assim) ou pelo fallback ex-idx
    const exSelecionado =
      exerciciosDisponiveis.find((ex) => String(ex._id) === exercicioSelecionadoId) ||
      exerciciosDisponiveis.find((ex) => String(ex._id?.$oid) === exercicioSelecionadoId) ||
      exerciciosDisponiveis.find((ex, i) => `ex-${i}` === exercicioSelecionadoId);

    if (!exSelecionado) {
      // se não encontrou, não fazemos reset massivo — apenas asseguramos estado consistente
      console.warn("Exercício seleccionado não encontrado", exercicioSelecionadoId);
      return;
    }

    setDadosExercicioSelecionado(exSelecionado);
    setType(tipoSelecionado);

    const steps = Array.isArray(exSelecionado.steps) ? exSelecionado.steps : [];

    // normalizar typeOfProcessing para um array de strings
    const rawTypeProc = exSelecionado.typeOfProcessing || [];
    const normalizedTypeProc = Array.isArray(rawTypeProc)
      ? rawTypeProc.map((item) => {
          if (typeof item === "string") return item;
          if (item && typeof item === "object") {
            // pode vir { label, value } ou { value } etc.
            return item.value ?? item.label ?? String(item);
          }
          return String(item);
        })
      : [];

    // usar replace para steps e setValue para os campos simples
    if (typeof replace === "function") {
      replace(steps);
      setValue("name", exSelecionado.name || "");
      setValue("description", exSelecionado.description || "");
      setValue("typeOfProcessing", normalizedTypeProc);
      setValue("tipo", tipoSelecionado);
      setValue("userId", id);
    } else {
      reset({
        userId: id,
        tipo: tipoSelecionado,
        name: exSelecionado.name || "",
        description: exSelecionado.description || "",
        typeOfProcessing: normalizedTypeProc,
        steps,
      });
    }
  }, [exercicioSelecionadoId, exerciciosDisponiveis, replace, reset, setValue, id, tipoSelecionado]);

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Adicionar Exercício</DialogTitle>
        </DialogHeader>

        {loading ? (
          <div className="flex justify-center py-10">
            <Loader2 className="animate-spin w-6 h-6" />
          </div>
        ) : (
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <input type="hidden" {...register("userId")} />

            {/* Seleção do tipo */}
            <Select
              value={tipoSelecionado}
              onValueChange={(v) => {
                setValue("tipo", v);
                setType(v);
                setExercicioSelecionadoId(""); // limpa seleção
              }}
            >
              <SelectTrigger>
                <SelectValue placeholder="Selecione o tipo de exercício" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="palavras">Repetição de Palavras</SelectItem>
                <SelectItem value="frases">Repetição de Frases</SelectItem>
                <SelectItem value="leitura">Atividades de Leitura</SelectItem>
                <SelectItem value="discurso">Discurso Espontâneo</SelectItem>
                <SelectItem value="diadococinesia">Diadococinésia</SelectItem>
                <SelectItem value="novo">Novo</SelectItem>
              </SelectContent>
            </Select>

            {/* {tipoSelecionado && Array.isArray(exerciciosDisponiveis) && exerciciosDisponiveis.length > 0 && (
              <Select
                value={exercicioSelecionadoId}
                onValueChange={(v) => setExercicioSelecionadoId(v)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Selecionar exercício existente" />
                </SelectTrigger>
                <SelectContent>
                  {exerciciosDisponiveis.map((ex, idx) => {
                    const key = ex._id ? ex._id.toString() : `ex-${idx}`;
                    const value = ex._id ? ex._id.toString() : `ex-${idx}`;
                    const name = ex.name || `Exercício ${idx + 1}`;
                    return (
                      <SelectItem key={key} value={value}>
                        {name}
                      </SelectItem>
                    );
                  })}
                </SelectContent>
              </Select>
            )} */}

            {tipoSelecionado && Array.isArray(exerciciosDisponiveis) && exerciciosDisponiveis.length > 0 && (
              <Select
                value={exercicioSelecionadoId || undefined}
                onValueChange={(v) => {
                  // alguns Selects (ou wrappers) por vezes enviam arrays — normalizamos
                  const raw = Array.isArray(v) ? (v.length > 0 ? v[0] : "") : v;
                  const selected = raw == null ? "" : String(raw);
                  setExercicioSelecionadoId(selected);
                }}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Selecionar exercício existente" />
                </SelectTrigger>
                <SelectContent>
                  {exerciciosDisponiveis.map((ex, idx) => {
                    const key = ex._id ? String(ex._id.$oid) : `ex-${idx}`;
                    const value = ex._id ? String(ex._id.$oid) : `ex-${idx}`;
                    const name = ex.name || `Exercício ${idx + 1}`;
                    return (
                      <SelectItem key={key} value={value}>
                        {name}
                      </SelectItem>
                    );
                  })}
                </SelectContent>
              </Select>
            )}

            {dadosExercicioSelecionado && (
              <Select value={modoEdicao} onValueChange={setModoEdicao}>
                <SelectTrigger>
                  <SelectValue placeholder="Modo de uso" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="default">
                    Usar exercício como está
                  </SelectItem>
                  <SelectItem value="personalizar">
                    Personalizar exercício
                  </SelectItem>
                </SelectContent>
              </Select>
            )}

            {/* Novo exercício */}
            {!dadosExercicioSelecionado && (
              <>
                <ExerciseMetaFields
                  register={register}
                  errors={errors}
                  control={control}
                  options={options}
                  appendStep={appendStep}
                />
                <ExerciseSteps
                  type={type}
                  fields={fields}
                  camposPorTipo={camposPorTipo}
                  camposPorTipoEn={camposPorTipoEn}
                  editable
                  register={register}
                  remove={remove}
                  appendStep={appendStep}
                />
              </>
            )}

            {/* Exercício existente */}
            {dadosExercicioSelecionado && (
              <ExerciseSelectedDetails
                dadosExercicioSelecionado={dadosExercicioSelecionado}
                modoEdicao={modoEdicao}
                setDadosExercicioSelecionado={setDadosExercicioSelecionado}
                control={control}
                options={options}
                errors={errors}
                type={type}
                camposPorTipo={camposPorTipo}
                camposPorTipoEn={camposPorTipoEn}
                register={register}
                remove={remove}
                appendStep={appendStep}
                fields={fields}
              />
            )}

            <DialogFooter className="flex justify-between">

              <Button type="submit" className="rounded">
                <PlusCircle size={16} /> Salvar Exercício
              </Button>

               <Button type="button" variant="secondary" className="rounded" onClick={onClose}>
                <XCircle size={16} /> Fechar
              </Button>
            </DialogFooter>
          </form>
        )}
      </DialogContent>
    </Dialog>
  );
}
