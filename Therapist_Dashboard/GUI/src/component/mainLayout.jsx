
import {useLocation } from "react-router-dom";
import { Outlet } from "react-router-dom";
import UtenteExerciseTab from "./utenteExerciseTab.jsx";
import LabTabs from "./labTabs.jsx";
export default function MainLayout() {
  const location = useLocation();
  const showUtenteExerciseTab = location.pathname.startsWith("/utente") || location.pathname.startsWith("/exercicios/genericos");

  return (
    <>
      <LabTabs />
      {showUtenteExerciseTab && <UtenteExerciseTab />}
      <div className="w-full px-0 top-6/12">
        <Outlet />
      </div>
    </>
  );
}

// import { Outlet, useLocation } from "react-router-dom";
// import LabTabs from "./LabTabs";
// import UtenteExerciseTab from "./UtenteExerciseTab";

// export default function MainLayout() {
//   const location = useLocation();
//   const showUtenteExerciseTab =
//     location.pathname.startsWith("/utente") ||
//     location.pathname.startsWith("/exercicios/genericos");

//   const hideAllTabs = location.pathname.startsWith("/utente/");

// //   if (hideAllTabs) {
// //     return <Outlet />;
// //   }

//   return (
//     <>
//       <LabTabs />
//       {showUtenteExerciseTab && <UtenteExerciseTab />}
//       <div style={{ paddingTop: "100px" }}>
//         {/* Espaço extra para evitar sobreposição com tabs fixos */}
//         <Outlet />
//       </div>
//     </>
//   );
// }

