import { Tab, Tabs, Box } from "@mui/material";
import TabList from "@mui/lab/TabList";
import TabContext from "@mui/lab/TabContext";
import { useNavigate, useParams, useLocation, Link  } from "react-router-dom";

export default function UtenteTabs() {
  const { id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();

  const path = location.pathname;

  let value = "1"; // padrão: Informação
  if (path.includes("/analise/articulacao")) value = "2";
  else if (path.includes("/analise/fonacao")) value = "3";
  // else if (path.includes("/analise/glota")) value = "4";
  else if (path.includes("/analise/prosodia")) value = "5";
  // else if (path.includes("/analise/fonologica")) value = "6";
  // else if (path.includes("/analise/reaprendizagem")) value = "7";
  else if (path.includes("/reabilitacao")) value = "7";
  else if (path.includes("/exercicios")) value = "8";

  const handleChange = (event, newValue) => {
    if (newValue === "1") navigate(`/utente/${id}/informacao`);
    if (newValue === "2") navigate(`/utente/${id}/analise/articulacao`);
    if (newValue === "3") navigate(`/utente/${id}/analise/fonacao`);
    // if (newValue === "4") navigate(`/utente/${id}/analise/glota`);
    if (newValue === "5") navigate(`/utente/${id}/analise/prosodia`);
    // if (newValue === "6") navigate(`/utente/${id}/analise/fonologica`);
    // if (newValue === "7") navigate(`/utente/${id}/analise/reaprendizagem`);
    if (newValue === "7") navigate(`/utente/${id}/reabilitacao`);
    // if (newValue === "7") navigate(`/utente/${id}/adicionar_exercicio`);
    if (newValue === "8") navigate(`/utente/${id}/exercicios`);
  };

  return (
    <Box sx={{
        borderBottom: 1,
        borderColor: 'divider',
        width: '100%', // largura total
        px: 0,
        border: '1px solid gray'
      }}
      className="px-0 w-full"
    >
      <TabContext value={value}>
        <TabList onChange={handleChange}
  aria-label="Utente Tabs"
  variant="fullWidth"
  sx={{ px: 0, width: "100%" }}>
          <Tab label="Informação" value="1"sx={{
              color: 'rgba(255, 255, 255, 0.6)', // não selecionado
              '&.Mui-selected': {
                color: 'lightgreen', // verde claro quando ativo
              },
            }} />
          <Tab label="Articulação" value="2" sx={{
              color: 'rgba(255, 255, 255, 0.6)', // não selecionado
              '&.Mui-selected': {
                color: 'lightgreen',
              },
            }} />
          <Tab label="Fonação" value="3" sx={{
              color: 'rgba(255, 255, 255, 0.6)', // não selecionado
              '&.Mui-selected': {
                color: 'lightgreen',
              },
            }} />
          {/* <Tab label="Glota" value="4" sx={{
              color: 'rgba(255, 255, 255, 0.6)', // não selecionado
              '&.Mui-selected': {
                color: 'lightgreen',
              },
            }} /> */}
          <Tab label="Prosódia" value="5" sx={{
              color: 'rgba(255, 255, 255, 0.6)', // não selecionado
              '&.Mui-selected': {
                color: 'lightgreen',
              },
            }}/>
          {/* <Tab label="Fonológica" value="6" sx={{
              color: 'rgba(255, 255, 255, 0.6)', // não selecionado
              '&.Mui-selected': {
                color: 'lightgreen',
              },
            }}/> */}
          <Tab label="Reabilitação" value="7" sx={{
              color: 'rgba(255, 255, 255, 0.6)', // não selecionado
              '&.Mui-selected': {
                color: 'lightgreen',
              },
            }}/>

          {/* <Tab label="Reaprendizagem" value="7" sx={{
              color: 'rgba(255, 255, 255, 0.6)', // não selecionado
              '&.Mui-selected': {
                color: 'lightgreen',
              },
            }}/> */}

          <Tab label="Exercícios" value="8" sx={{
              color: 'rgba(255, 255, 255, 0.6)', // não selecionado
              '&.Mui-selected': {
                color: 'lightgreen',
              },
            }} />
        </TabList>
      </TabContext>
    </Box>
  );
};
