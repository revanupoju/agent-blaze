import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Blaze — AI Marketing Agent for Apollo Cash",
  description: "Three-agent AI marketing system powering Apollo Cash growth",
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
