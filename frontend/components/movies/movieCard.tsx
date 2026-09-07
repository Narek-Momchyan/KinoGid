import React from 'react';
import Link from 'next/link';
import { Movie } from '@/types/movieType';
import { getMediaUrl } from '@/lib/media';

interface MovieCardProps {
    movie: Movie;
    lang: string;
}

export default function MovieCard({ movie, lang }: MovieCardProps) {
    let title = movie[`title_${lang as 'am'|'ru'|'en'}`] || movie.title_en || movie.title_am;
    const posterUrl = getMediaUrl(movie.poster);

    return (
        <Link href={`/movies/${movie.slug}`} className="cursor-pointer group relative rounded-xl overflow-hidden shadow-lg shadow-black/50 bg-gray-900 border border-gray-800 hover:border-cyan-500/50 hover:shadow-[0_0_20px_rgba(6,182,212,0.3)] transition-all duration-300 flex flex-col">
            <div className="relative aspect-[2/3] w-full">
                {posterUrl ? (
                    <img 
                        src={posterUrl} 
                        alt={title}
                        className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                    />
                ) : (
                    <div className="w-full h-full bg-gray-800 flex items-center justify-center text-gray-600 transition-transform duration-500 group-hover:scale-110">
                        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round">
                            <rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"></rect>
                            <line x1="7" y1="2" x2="7" y2="22"></line>
                            <line x1="17" y1="2" x2="17" y2="22"></line>
                            <line x1="2" y1="12" x2="22" y2="12"></line>
                        </svg>
                    </div>
                )}
                <div className="absolute inset-0 bg-gradient-to-t from-black via-black/40 to-transparent opacity-80 group-hover:opacity-60 transition-opacity duration-300"></div>
                
                {movie.views_count > 0 && (
                    <div className="absolute top-2 right-2 bg-black/60 backdrop-blur-sm text-xs font-bold text-white px-2 py-1 rounded flex items-center gap-1 border border-gray-700/50">
                        <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-cyan-400">
                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                            <circle cx="12" cy="12" r="3"></circle>
                        </svg>
                        {movie.views_count}
                    </div>
                )}
            </div>
            
            <div className="p-4 relative flex-1 flex flex-col justify-between z-10 bg-gradient-to-t from-black to-transparent">
                <h3 className="text-lg font-bold text-white line-clamp-2 drop-shadow-md group-hover:text-cyan-400 transition-colors">
                    {title}
                </h3>
                
                <div className="flex items-center justify-between mt-3 text-xs text-gray-300 font-medium">
                    <span className="bg-[#E50914] text-white px-2 py-0.5 rounded shadow-[0_0_8px_rgba(229,9,20,0.5)]">
                        {movie.release_year}
                    </span>
                    <span className="flex items-center gap-1">
                        <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-cyan-500">
                            <circle cx="12" cy="12" r="10"></circle>
                            <polyline points="12 6 12 12 16 14"></polyline>
                        </svg>
                        {movie.duration} {lang === 'am' ? 'ր' : lang === 'ru' ? 'м' : 'm'}
                    </span>
                </div>
            </div>
            
          
            <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
                <div className="w-12 h-12 bg-red-600/90 rounded-full flex items-center justify-center shadow-[0_0_20px_rgba(229,9,20,0.6)] backdrop-blur-sm transform scale-50 group-hover:scale-100 transition-transform duration-300">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="white" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="ml-1">
                        <polygon points="5 3 19 12 5 21 5 3"></polygon>
                    </svg>
                </div>
            </div>
        </Link>
    );
}
