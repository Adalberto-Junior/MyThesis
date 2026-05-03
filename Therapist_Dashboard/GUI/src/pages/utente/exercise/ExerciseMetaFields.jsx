
import React from "react";
import { ErrorMessage } from "@hookform/error-message";
import { Controller } from "react-hook-form";
import { Input } from "../../../components/ui/input";
import { Textarea } from "../../../components/ui/textarea";
import { Button } from "../../../components/ui/button";
import { MultiSelect } from "primereact/multiselect";
import { PlusCircle } from "lucide-react";

export function ExerciseMetaFields({ register, errors, control, options, appendStep }) {
  return (
    <div className="space-y-4 rounded-xl border p-4 bg-muted/30">
      {/* Nome */}
      <div>
        <label className="block mb-1 font-medium">
          Nome do Exercício <span className="text-red-500">*</span>
        </label>
        <Input
          type="text"
          {...register("name", { required: "Nome do exercício é obrigatório." })}
        />
        <ErrorMessage
          errors={errors}
          name="name"
          render={({ message }) => <p className="text-red-500 text-sm">{message}</p>}
        />
      </div>

      {/* Descrição */}
      <div>
        <label className="block mb-1 font-medium">Descrição</label>
        <Textarea {...register("description")} />
        <ErrorMessage
          errors={errors}
          name="description"
          render={({ message }) => <p className="text-red-500 text-sm">{message}</p>}
        />
      </div>

      {/* Tipo de processamento */}
      <div>
        <label className="block mb-1 font-medium">
          Tipo de Processamento <span className="text-red-500">*</span>
        </label>
          {/* <Controller
            name="typeOfProcessing"
            control={control}
            rules={{
              required: "Selecione pelo menos um tipo de Processamento.",
              validate: (value) => value?.length > 0 || "Selecione pelo menos um tipo.",
            }}
            render={({ field }) => (
              <MultiSelect
                value={field.value || []}                 // garantir array
                options={options}
                optionLabel="label"
                optionValue="value"
                filter
                placeholder="Selecione os tipos"
                display="chip"
                className="w-full"
                onChange={(e) => field.onChange(e.value)} // importante: passar e.value
                onBlur={field.onBlur}
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
          render={({ message }) => <p className="text-red-500 text-sm">{message}</p>}
        />
      </div>

      {/* Botão de adicionar passos */}
      <div className="flex justify-end">
        <Button type="button" variant="outline" onClick={appendStep} className="flex gap-2 rounded">
          <PlusCircle size={16} /> Adicionar passo
        </Button>
      </div>
    </div>
  );
}
