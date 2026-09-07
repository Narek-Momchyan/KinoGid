import React from 'react'
import { getHeaderData } from '@/lib/api';
import { getLang } from '@/lib/lang';
import Logo from './logo';
import Navbar from './navbar';
import AIChatButton from './AIChatButton';
import Languages from './languages';
import { Metadata } from 'next';
export const metadata: Metadata = {
  title: "Header",
  description: "Header component",
};
export default async function Header() {
  const lang = await getLang();
  const headerData = await getHeaderData(lang);
  
  return (
    <div className="sticky top-4 z-50 px-4 w-full flex justify-center">
      <header className="w-full max-w-7xl backdrop-blur-xl bg-black/80 border border-slate-700/60 shadow-2xl shadow-black/40 rounded-full">
        <div className="flex justify-between items-center px-6 py-3">
          <Logo data={headerData?.logo} />
          <Navbar data={headerData?.navbar} />
          <div className='flex gap-2'>
            <AIChatButton  />
            <Languages data={headerData?.languages} lang={lang} />
          </div>
          
        </div>
      </header>
    </div>
  )
}
