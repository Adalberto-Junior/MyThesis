
import {useLocation } from "react-router-dom";
import UtenteExerciseTab from "./utenteExerciseTab.jsx";

export default function ConditionalUtenteExerciseTab() {
  const location = useLocation();
  
  // Mostra subtab apenas em /utentes ou /exercicios/genericos
  const showSubTab =
    location.pathname === "/" ||
    location.pathname === "/exercicios/genericos";

  return showSubTab ? <UtenteExerciseTab /> : null;
}
