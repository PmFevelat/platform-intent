import type { Metadata } from "next";
import "./globals.css";
import { LayoutContent } from "@/components/LayoutContent";

export const metadata: Metadata = {
  title: "presti.ai - Sales Intelligence",
  description: "Job analysis and sales intelligence for furniture industry",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-white">
        <LayoutContent>{children}</LayoutContent>
      </body>
    </html>
  );
}
