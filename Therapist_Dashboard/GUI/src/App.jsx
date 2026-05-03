
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { useState } from "react";
import { Navigate } from "react-router-dom";
import RegisterForm from './pages/auth/registerForm.jsx'
import NoPage from './pages/NoPage.jsx'
import LoginForm from './pages/auth/login.jsx'
// import Home from './pages/Home.jsx'
import LabTabs from "./component/labTabs.jsx";
// import UtenteExerciseTab from "./component/utenteExerciseTab.jsx";
import ConditionalUtenteExerciseTab from "./component/ConditionalUtenteExerciseTab.jsx";
import AllUtente from './pages/utente/utenteData/all_utente.jsx'
import Profile from './pages/therapist/perfil.jsx'
import HealthUserInformation from './pages/utente/utenteData/information.jsx'
// import ArticulationResult from './pages/utente/result/versao1/articulation.jsx'
// import ProsodyResult from './pages/utente/result/versao1/prosody.jsx'
// import PhonotionResult from './pages/utente/result/versao1/phonation.jsx'
// import GlottalResult from './pages/utente/result/versao1/glottal.jsx'
// import ReplearningResult from './pages/utente/result/versao1/repleaning.jsx'
// import PhonologicalResult from "./pages/utente/result/versao1/phonological.jsx"; 
import AllExercise from './pages/utente/exercise/allExercise.jsx'
import AllGenericExercise from './pages/utente/exercise/allExerciseGeneric.jsx'
import ExerciseDetail from './pages/utente/exercise/exerciseDetail.jsx'
import EditUtente from './pages/utente/utenteData/editUtent.jsx'
import EditarExercicioForm from './pages/utente/exercise/editExercise.jsx'
import ReportList from './pages/utente/utenteData/allReport.jsx'
import EditReport from "./pages/utente/utenteData/editReport.jsx";
import ArticulationResultPage from './pages/utente/result/versao2/articulationPage.jsx'
import ProsodyResultPage from "./pages/utente/result/versao2/prosodyPage.jsx";  
import PhonotionResultPage from "./pages/utente/result/versao2/phonationPage.jsx";
import GenericExerciseDetail from "./pages/utente/exercise/GenericExerciseDetail.jsx";
import EditarGenericExercicioForm from "./pages/utente/exercise/editGenericExercise.jsx";
import UtenteTabsLayout from "./layouts/UtenteTabsLayout";
import ExerciseForm from "./pages/utente/reabilitation/exerciseForm.jsx";
import ExerciseList from "./pages/utente/reabilitation/ExercisesList.jsx";
import ExerciseDetails from "./pages/utente/reabilitation/ExerciseDetails.jsx";
import ExerciseEdit from "./pages/utente/reabilitation/ExerciseEdit.jsx"; 

function ProtectedRoute({ children }) {
  const token = localStorage.getItem("token");

  if (!token) {
    return <Navigate to="/login" />;
  }

  return children;
}

export default function App() {
  // const isAuth = localStorage.getItem('token') !== null && localStorage.getItem('token') !== "";
  
  const [isAuth, setIsAuth] = useState(
    !!localStorage.getItem("token")
  );

  return (
    <BrowserRouter>
      {isAuth && <LabTabs />}
      {isAuth && <ConditionalUtenteExerciseTab />}

      <Routes>
         {/* ROOT */}
        <Route 
          path="/" 
          element={isAuth ? <AllUtente /> : <Navigate to="/login" />} 
        />

        {/* ROTAS PUBLICAS */}
        <Route path="/login" element={<LoginForm setIsAuth={setIsAuth}  />} />
        <Route path="/register" element={<RegisterForm />} />

        {/* ROTAS PROTEGIDAS */}
        {isAuth && (
          <>
            <Route path="/" 
              element={<ProtectedRoute>
                <AllUtente />
                </ProtectedRoute>
              } 
            />
            <Route path="exercicios/genericos" element={<AllGenericExercise />} />
              <Route path="exercicios/genericos/detail/:id" element={<GenericExerciseDetail />} />
              <Route path="exercicios/genericos/detail/editar/:id" element={<EditarGenericExercicioForm />} />

            <Route path="me" element={<Profile setIsAuth={setIsAuth} />} />
            <Route path="utente/:id" element={<UtenteTabsLayout />}>
              <Route path="informacao" element={<HealthUserInformation />} />
              <Route path="relatorio" element={<ReportList />} />
              <Route path="relatorio/edit/:id_" element={<EditReport />} />
              <Route path="editar" element={<EditUtente />} />
              <Route path="analise/articulacao" element={<ArticulationResultPage />} />
              {/* <Route path="analise/articulacao" element={<ArticulationResult />} /> */}
              <Route path="analise/fonacao" element={<PhonotionResultPage />} />
              {/* <Route path="analise/fonacao" element={<PhonotionResult />} /> */}
              {/* <Route path="analise/prosodia" element={<ProsodyResult />} /> */}
              <Route path="analise/prosodia" element={<ProsodyResultPage />} />
              {/* <Route path="analise/glota" element={<GlottalResult />} />
              <Route path="analise/fonologica" element={<PhonologicalResult />} /> */}
              {/* <Route path="analise/reaprendizagem" element={<ReplearningResult/>} /> */}
              <Route path="reabilitacao" element={<ExerciseList />} />
              <Route path="reabilitacao/novo-exercicio" element={<ExerciseForm />} />  
              <Route path="reabilitacao/exercicio/:exerciseId" element={<ExerciseDetails />} />
              <Route path="reabilitacao/exercicio/editar/:exerciseId" element={<ExerciseEdit />} />
              <Route path="exercicios" element={<AllExercise />} />
              <Route path="exercicio/:id_" element={<ExerciseDetail />} />
              <Route path="exercicio/editar/:id_" element={<EditarExercicioForm />} />
            </Route>
          </>
        )}

        <Route path="*" element={<NoPage />} />

      </Routes>
    </BrowserRouter>
  );
}
