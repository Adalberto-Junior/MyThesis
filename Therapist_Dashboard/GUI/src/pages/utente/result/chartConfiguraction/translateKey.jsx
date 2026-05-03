
const baseTranslations = {
  static_result: "Resultados Estáticos",
  no_static_result: "Resultados não Estáticos",
  $oid: "ID do Objeto",
  id: "Identificador",
  date: "Data",
  // BBEon_BBEoff: "BBEon&BBEoff",
};

const componentDescriptions = {
  BBEon: "Energias de banda de casca em transições de início",
  BBEoff: "Energias de banda de casca em transições de fim",
  MFCCoff: "Coeficientes cepstrais em transições de fim",
  MFCCon: "Coeficientes cepstrais em transições de início",
  DMFCCoff: "Coeficientes cepstrais dinâmicos em transições de fim",
  DMFCCon: "Coeficientes cepstrais dinâmicos em transições de início",
  DDMFCCoff: "Coeficientes cepstrais dinâmicos de segunda derivada em transições de fim",
  DDMFCCon: "Coeficientes cepstrais dinâmicos de segunda derivada em transições de início",
  F1: "Primeiro Formante",
  F2: "Segundo Formante",
  F3: "Terceiro Formante",
  F4: "Quarto Formante",
  Apq: "Quociente de perturbação da amplitude"

};

const prefixTranslations = {
  avg: "Média de",
  std: "Desvio padrão de",
  Avg: "Média de",
  skewness: "Assimetria de",
  kurtosis: "Curtose de", 
};

export function translateKey(key) {
  // Traduções diretas
  if (baseTranslations[key]) return baseTranslations[key];
  if (key.startsWith("no_static_result")) return baseTranslations.no_static_result;
  // Padrões tipo "avg BBEon_1" ou "dst MFCCoff_2"
  const pattern = /^(avg|std|skewness|kurtosis|Avg) ([A-Za-z]+)_(\d+)$/;
  const match = key.match(pattern);
  if (match) {
    const [, prefix, component, number] = match;
    const prefixText = prefixTranslations[prefix] || prefix;
    const componentText = componentDescriptions[component] || component;
    return `${prefixText} ${componentText} ${number} (${component} ${number})`;
  }

  // Fallback: tornar legível qualquer outra chave
  return key.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase());
}

