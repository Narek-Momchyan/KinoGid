'use client'

import React from 'react';
import { LanguageItem } from '@/types/headerType';

export default function Languages({ data, lang }: { data?: LanguageItem[], lang: string }) {
    const onchange = (code: string) => {
        const date = new Date()
        date.setFullYear(date.getFullYear() + 10)
        if (typeof document !== 'undefined') {
            document.cookie = `lang=${code}; path=/;expires=${date.toUTCString()}`
        }
        if (typeof window !== 'undefined') {
            window.location.reload()
        }
    }

    return (
        <div className="relative group">
 
            <button className=" cursor-pointer flex items-center justify-center p-2 rounded-full text-gray-300 hover:text-white bg-gray-900/50 hover:bg-gray-800 border border-gray-700/50 hover:border-red-500/50 transition-all duration-300 hover:shadow-[0_0_15px_rgba(220,38,38,0.3)]">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="2" y1="12" x2="22" y2="12"></line>
                    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
                </svg>
            </button>

 
            <div className="absolute right-0 top-full pt-4 hidden group-hover:block z-50 w-24 animate-in fade-in slide-in-from-top-2 duration-300">
                <div className="bg-gray-900/90 backdrop-blur-xl border border-gray-700/50 rounded-xl shadow-[0_0_20px_rgba(37,99,235,0.15)] overflow-hidden flex flex-col p-2 gap-2">
                    {data?.map((l: any) => (
                        <button 
                            key={l.id} 
                            onClick={() => onchange(l.name)}
                            className={` cursor-pointer
                                relative px-3 py-1.5 rounded-lg text-sm font-bold transition-all duration-300 uppercase tracking-wider overflow-hidden w-full text-center
                                ${lang === l.name 
                                    ? 'text-white bg-linear-to-r from-blue-600 to-blue-800 shadow-[0_0_15px_rgba(37,99,235,0.5)] border border-blue-500/50' 
                                    : 'text-gray-400 hover:text-white hover:bg-gray-800/50 border border-transparent hover:border-red-500/50 hover:shadow-[0_0_10px_rgba(220,38,38,0.2)]'}
                            `}
                        >
                            {l.name}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
}