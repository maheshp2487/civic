import Link from "next/link";
import { Scale } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-border-subtle bg-surface mt-auto">
      <div className="container mx-auto px-6 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="md:col-span-2 space-y-4">
            <div className="flex items-center gap-2 mb-4 text-text-primary">
              <Scale className="w-6 h-6 text-accent-primary" />
              <span className="font-semibold tracking-tight">VidhiSetu</span>
            </div>
            <p className="text-text-secondary text-sm leading-relaxed">
              Navigate your legal situation with clarity. We help you understand your context, find relevant official information, and plan your next steps safely.
            </p>
          </div>
          
          <div>
            <h3 className="font-semibold text-text-primary mb-4 text-sm">Product</h3>
            <ul className="space-y-3 text-sm text-text-secondary">
              <li><Link href="/" className="hover:text-accent-primary transition-colors">Start a Case</Link></li>
              <li><Link href="/" className="hover:text-accent-primary transition-colors">How it Works</Link></li>
              <li><Link href="/" className="hover:text-accent-primary transition-colors">Documentation</Link></li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold text-text-primary mb-4 text-sm">Trust</h3>
            <ul className="space-y-3 text-sm text-text-secondary">
              <li><Link href="/" className="hover:text-accent-primary transition-colors">Safety</Link></li>
              <li><Link href="/" className="hover:text-accent-primary transition-colors">Privacy</Link></li>
              <li><span className="text-text-muted">Disclaimer: Not legal advice.</span></li>
            </ul>
          </div>
        </div>
        
        <div className="mt-12 pt-8 border-t border-border-subtle flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-xs text-text-muted">
            &copy; {new Date().getFullYear()} VidhiSetu Legal Navigation. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
