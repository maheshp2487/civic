"use client";
// ThemeProvider is no longer needed — the design is a fixed light/warm palette
// with a dark sidebar embedded in the case workspace.
import * as React from "react";

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
