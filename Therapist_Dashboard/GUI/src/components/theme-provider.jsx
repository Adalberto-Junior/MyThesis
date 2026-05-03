"use client"

import * as React from "react"
import { ThemeProvider as NextThemesProvider } from "next-themes"

export default function ThemeProvider({ children, ...props }) {
  // return <NextThemesProvider {...props}>{children}</NextThemesProvider>
  return (
    <NextThemesProvider
      attribute="class"            // <- aplica "dark" no <html>
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
      {...props}
    >
      {children}
    </NextThemesProvider>
  );
}
