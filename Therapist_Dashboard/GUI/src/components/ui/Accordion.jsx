import { useState } from "react";
import { ChevronDown } from "lucide-react";

export function Accordion({ children, defaultOpen = false, className = "" }) {
  return <div className={`space-y-2 ${className}`}>{children}</div>;
}

export function AccordionItem({ title, children, defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className="border border-gray-300 dark:border-zinc-700 rounded-xl overflow-hidden shadow-sm">
      <button
        className="flex justify-between items-center w-full px-4 py-3 bg-gray-100 dark:bg-zinc-800 dark:text-white text-left font-semibold text-lg hover:bg-gray-200 dark:hover:bg-zinc-700 transition"
        onClick={() => setOpen(!open)}
      >
        <span>{title}</span>
        <ChevronDown
          className={`h-5 w-5 transition-transform ${open ? "rotate-180" : ""}`}
        />
      </button>
      {open && (
        <div className="px-4 py-3 bg-white dark:bg-zinc-900 dark:text-gray-200">
          {children}
        </div>
      )}
    </div>
  );
}

export function AccordionTrigger({ children, toggle }) {
  return (
    <button
      onClick={toggle}
      className="w-full text-left px-4 py-2 bg-gray-100 dark:bg-zinc-800 hover:bg-gray-200 dark:hover:bg-zinc-700 font-semibold"
    >
      {children}
    </button>
  );
}

export function AccordionContent({ children, isOpen }) {
  return (
    <div
      className={`transition-all duration-300 ease-in-out ${
        isOpen ? "max-h-screen p-4" : "max-h-0 overflow-hidden"
      }`}
    >
      {children}
    </div>
  );
}