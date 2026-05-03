import { Outlet } from "react-router-dom";
import UtenteTabs from "../component/utenteTabs.jsx";

export default function UtenteTabsLayout() {
  return (
    <div className="min-h-screen bg-gray-500 dark:bg-zinc-900 px-0 mt-11">
      <UtenteTabs />
      <div className="w-full px-0">
        <Outlet />
      </div>
    </div>
  );
}