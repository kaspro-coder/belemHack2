import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DEFI RISK DEPENDENCY ANALYZER",
  description:
    "Analyze risk propagation across interconnected DeFi protocol layers.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="font-mono antialiased">{children}</body>
    </html>
  );
}
