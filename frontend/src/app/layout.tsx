import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { TopNav } from "@/components/layout/TopNav";
import { Footer } from "@/components/layout/Footer";
import { Providers } from "./providers";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "GitScribe | AI Git Commit & PR Generator",
  description: "Generate conventional commit messages and professional PR descriptions from git diffs.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} h-full antialiased`}>
      <body className="font-inter font-raycast bg-canvas text-body antialiased min-h-screen flex flex-col">
        <Providers>
          <TopNav />
          {children}
          <Footer />
        </Providers>
      </body>
    </html>
  );
}
