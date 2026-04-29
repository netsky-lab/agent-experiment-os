import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Agent Experiment OS Dashboard",
  description:
    "Product dashboard for MCP-native experiment knowledge, agent runs, review queues, and provenance.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
