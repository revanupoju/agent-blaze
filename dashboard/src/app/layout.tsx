import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Agent Blaze — AI Marketing Platform",
  description: "Four AI agents powering Apollo Cash marketing — Vortex, Draft, Rally, Freq",
  icons: {
    icon: "/blaze-logo.png",
    apple: "/blaze-logo.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col bg-background text-foreground">
        {children}
      </body>
    </html>
  );
}
