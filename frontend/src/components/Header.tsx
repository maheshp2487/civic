import { Scale } from "lucide-react";
import Link from "next/link";
import { ThemeToggle } from "./ThemeToggle";

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-border-subtle bg-surface/80 backdrop-blur-md">
      <div className="container mx-auto px-6 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 text-text-primary hover:opacity-80 transition-opacity">
          <Scale className="w-6 h-6 text-accent-primary" />
          <span className="font-semibold text-lg tracking-tight">VidhiSetu</span>
        </Link>
        
        <div className="flex items-center gap-4">
          <ThemeToggle />
          <Link 
            href="/"
            className="hidden md:inline-flex px-4 py-2 bg-accent-primary hover:bg-accent-hover text-white text-sm font-medium rounded-lg transition-colors"
          >
            New Case
          </Link>
        </div>
      </div>
    </header>
  );
}
