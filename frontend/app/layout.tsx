import type { Metadata } from "next";
import "./globals.css";
import Header from "@/components/header";
import AIChat from "@/components/ai_search/AIChat";
export const metadata: Metadata = {
  title: "KinoGid",
  description: "watch movies online for free",
};

import { getLang } from "@/lib/lang";

export default async function RootLayout({ children }: LayoutProps<"/">) {
  const lang = await getLang();

  return (
    <html lang={lang}>
      <body className=" bg-black">
        <Header />
        {children}
        <AIChat lang={lang as 'en' | 'am' | 'ru'} />
      </body>
    </html>
  );
}
