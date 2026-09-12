import type { Metadata } from "next";
import { EB_Garamond, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const ebGaramond = EB_Garamond({
  subsets: ["latin"],
  variable: "--font-untitled-serif",
  weight: ["400"],
  style: ["normal", "italic"],
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-abc-diatype-mono",
  weight: ["400", "500"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "VARIDHI — Marine Intelligence & Ocean Reasoning Platform",
  description: "ISRO SIH 26176 — Editorial tech journal on warm parchment for marine intelligence, coastal safety, and operational oceanography.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${ebGaramond.variable} ${jetbrainsMono.variable}`}>
      <body
        style={{
          backgroundColor: "#f6f3f1",
          color: "#242424",
          fontFamily: "var(--font-abc-diatype-mono), ui-monospace, monospace",
        }}
      >
        {children}
      </body>
    </html>
  );
}
