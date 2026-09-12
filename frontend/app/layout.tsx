import type { Metadata } from "next";
import { Inter, EB_Garamond, JetBrains_Mono } from "next/font/google";
import "./globals.css";

// Primary UI font — clean, modern sans-serif
const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  weight: ["400", "500", "600", "700"],
  display: "swap",
});

// Display/editorial serif — for headings and branding
const ebGaramond = EB_Garamond({
  subsets: ["latin"],
  variable: "--font-untitled-serif",
  weight: ["400"],
  style: ["normal", "italic"],
  display: "swap",
});

// Monospace — only for data values, code, metric numbers
const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-abc-diatype-mono",
  weight: ["400", "500"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "VARIDHI — Marine Intelligence & Ocean Reasoning Platform",
  description:
    "ISRO SIH 26176 — Agentic AI for marine intelligence, coastal safety, and operational oceanography.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${ebGaramond.variable} ${jetbrainsMono.variable}`}
    >
      <body
        style={{
          backgroundColor: "#f6f3f1",
          color: "#242424",
          fontFamily: "var(--font-inter), ui-sans-serif, system-ui, sans-serif",
        }}
      >
        {children}
      </body>
    </html>
  );
}
