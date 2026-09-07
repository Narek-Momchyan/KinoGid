"use client";

import React, { useRef } from 'react';
import { useRouter, useSearchParams, usePathname } from 'next/navigation';

export default function Search({ lang }: { lang: string }) {
    const router = useRouter();
    const searchParams = useSearchParams();
    const pathname = usePathname();
    
    // Use a ref to store the timeout so we can clear it
    const timeoutRef = useRef<NodeJS.Timeout | null>(null);

    const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
        const val = e.target.value;

        if (timeoutRef.current) {
            clearTimeout(timeoutRef.current);
        }

        timeoutRef.current = setTimeout(() => {
            const current = new URLSearchParams(Array.from(searchParams.entries()));
            
            if (val.trim()) {
                current.set('search', val.trim());
            } else {
                current.delete('search');
            }
            
            // Always reset to page 1 on new search
            current.set('page', '1');
            
            const search = current.toString();
            const queryUrl = search ? `?${search}` : '';
            
            router.push(`${pathname}${queryUrl}`, { scroll: false });
        }, 400); // 400ms debounce
    };

    const placeholderText = lang === 'am' ? 'Որոնել ֆիլմեր...' : lang === 'ru' ? 'Поиск фильмов...' : 'Search movies...';

    return (
        <div className="relative w-full max-w-sm">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-gray-400">
                    <circle cx="11" cy="11" r="8"></circle>
                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>
            </div>
            <input 
                type="text" 
                defaultValue={searchParams.get('search') || ''}
                onChange={handleSearch}
                placeholder={placeholderText}
                className="w-full bg-gray-900 border border-gray-700 text-white rounded-full py-2 pl-10 pr-4 focus:outline-none focus:border-red-500 focus:ring-1 focus:ring-red-500 transition-colors shadow-inner shadow-black/50"
            />
        </div>
    );
}
