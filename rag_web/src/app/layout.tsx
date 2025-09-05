import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "PharmaRAG - AI Pharmaceutical Assistant",
  description: "AI-powered pharmaceutical information and medication assistant",
  icons: {
    icon: '/bot.png',
    shortcut: '/bot.png',
    apple: '/bot.png',
  },
  manifest: '/manifest.json',
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
    userScalable: false,
  },
  openGraph: {
    title: "PharmaRAG - AI Pharmaceutical Assistant",
    description: "AI-powered pharmaceutical information and medication assistant",
    images: ['/bot.png'],
  },
  twitter: {
    card: 'summary_large_image',
    title: "PharmaRAG - AI Pharmaceutical Assistant",
    description: "AI-powered pharmaceutical information and medication assistant",
    images: ['/bot.png'],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
