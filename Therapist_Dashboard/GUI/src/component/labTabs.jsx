import * as React from "react";
import Box from "@mui/material/Box";
import Tab from "@mui/material/Tab";
import TabContext from "@mui/lab/TabContext";
import TabList from "@mui/lab/TabList";
import { useNavigate, useLocation } from "react-router-dom";

// export default function LabTabs() {
//   const location = useLocation();
//   const navigate = useNavigate();

//   const getTabValueFromPath = () => {
//     if (location.pathname.startsWith("/utentes")) return "2";
//     if (location.pathname.startsWith("/me")) return "3";
//     return "1";
//   };

//   const [value, setValue] = React.useState(getTabValueFromPath());

//   React.useEffect(() => {
//     setValue(getTabValueFromPath());
//   }, [location.pathname]);

//   const handleChange = (event, newValue) => {
//     setValue(newValue);
//     if (newValue === "1") navigate("/");
//     if (newValue === "2") navigate("/utente");
//     if (newValue === "3") navigate("/me");
//   };

//   return (
//     <div className="z-50 fixed top-0 left-0 right-0 bg-white"
//       style={{
//         position: "fixed", // fixo no topo da tela
//         top: 0,
//         left: 0,
//         right:0,
//         width: "100%",
//         zIndex: 1000,
//         backgroundColor: "var(--mui-palette-background-default)", // fundo adaptável
//       }}
//     >
//       <Box sx={{ width: "100%", borderBottom: 1, borderColor: "divider" }}>
//         <TabContext value={value}>
//           <TabList
//               onChange={handleChange}
//               aria-label="Main Tabs"
//               variant="fullWidth"
//               sx={{ px: 0, width: "100%" }}
//             >
//             <Tab label="Home" value="1" />
//             <Tab label="Utente" value="2" />
//             <Tab label="Perfil" value="3" />
//           </TabList>
//         </TabContext>
//       </Box>
//     </div>
//   );
// }

export default function LabTabs() {
  const location = useLocation();
  const navigate = useNavigate();

  const getTabValueFromPath = () => {
    // if (location.pathname.startsWith("/utente") || location.pathname.startsWith("/exercicios")) return "1";
    if (location.pathname.startsWith("/me")) return "2";
    return "1";
  };

  const [value, setValue] = React.useState(getTabValueFromPath());

  React.useEffect(() => {
    setValue(getTabValueFromPath());
  }, [location.pathname]);

  const handleChange = (event, newValue) => {
    setValue(newValue);
    if (newValue === "1") navigate("/");
    // if (newValue === "2") navigate("/utentes");
    if (newValue === "2") navigate("/me");
  };

  return (
    <div className="z-50 fixed top-0 left-0 right-0 bg-white dark:bg-gray-600">
      <Box sx={{ width: "100%", borderBottom: 1, borderColor: "divider" }}>
        <TabContext value={value}>
          <TabList
            onChange={handleChange}
            aria-label="Main Tabs"
            variant="fullWidth"
            sx={{ px: 0, width: "100%" }}
          >
            {/* <Tab label="Home" value="1" /> */}
            <Tab label="Utente" value="1" />
            <Tab label="Perfil" value="2" />
          </TabList>
        </TabContext>
      </Box>
    </div>
  );
}
