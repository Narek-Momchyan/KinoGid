
import React from 'react';
import Link from 'next/link';
import { NavbarItem } from '@/types/headerType';

export default function Navbar({ data }: { data?: NavbarItem[] }) {
    return (
        <nav className="flex gap-8 items-center">
            {data?.map((item) => (
                <div key={item.id} className="relative group">
                    <Link href={item.href || '#'} className="relative block py-2 text-gray-300 font-medium tracking-wide transition-colors duration-300 group-hover:text-white after:content-[''] after:absolute after:-bottom-1 after:left-0 after:w-0 after:h-[2px] after:bg-gradient-to-r after:from-red-500 after:to-blue-500 after:transition-all after:duration-300 group-hover:after:w-full">
                        {item.title}
                    </Link>
                    {item.categories && item.categories.length > 0 && (
                        <div className="absolute left-0 top-full pt-4 hidden group-hover:block z-50 w-[450px] animate-in fade-in slide-in-from-top-2 duration-300">
                            <div className="bg-gray-900/95 backdrop-blur-xl border border-gray-700/50 rounded-xl shadow-[0_0_30px_rgba(37,99,235,0.2)] overflow-hidden">
                                <ul className="py-4 px-3 grid grid-cols-2 gap-x-3 gap-y-2 max-h-[60vh] overflow-y-auto scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-gray-800">
                                    {item.categories.filter((c, index, self) => self.findIndex(c2 => c2.slug === c.slug) === index).map((category) => (
                                        <li key={category.id}>
                                            <Link href={category.href || '#'} className="block px-3 py-2 text-sm text-gray-300 hover:text-white hover:bg-gradient-to-r hover:from-gray-800 hover:to-transparent transition-all duration-300 hover:pl-4 border-l-2 border-transparent hover:border-red-500 rounded">
                                                {category.name}
                                            </Link>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                    )}
                </div>
            ))}
        </nav>
    );
}
