import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "VidhiSetu — Legal Navigation",
  description:
    "Navigate your legal situation with clarity. Understand your legal context, identify relevant evidence, and map out next steps safely.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} h-full antialiased`}>
      <body className="h-full bg-page text-text-primary">
        {children}
      </body>
    </html>
  );
}
