import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { LogoData } from '@/types/headerType';

export default function Logo({ data }: { data: any }) {
    return (
        <Link href="/" className="group flex items-center gap-2"> 
            <div className="text-3xl font-black uppercase tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-red-600 via-red-500 to-blue-600 drop-shadow-[0_0_15px_rgba(220,38,38,0.5)] group-hover:drop-shadow-[0_0_25px_rgba(37,99,235,0.7)] transition-all duration-500">
                {data?.name || "KINO"}
            </div>
        </Link>
    );
}
