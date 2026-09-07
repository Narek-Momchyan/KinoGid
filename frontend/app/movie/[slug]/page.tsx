import React from 'react';
import { getMovieBySlug } from '@/lib/api';
import { getLang } from '@/lib/lang';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { getMediaUrl, getStreamUrl } from '@/lib/media';
import { translateText } from '@/lib/translate';
import MoviePlayer from '@/components/movies/MoviePlayer';

interface PageProps {
    params: Promise<{ slug: string }>;
}

export default async function MovieDetailPage({ params }: PageProps) {
    const { slug } = await params;
    const lang = await getLang();
    const movie = await getMovieBySlug(slug);

    if (!movie) {
        return notFound();
    }

    let title = movie[`title_${lang as 'am'|'ru'|'en'}`] || movie.title_en || movie.title_am;
    let description = movie[`description_${lang as 'am'|'ru'|'en'}`] || movie.description_en || movie.description_am;

    const needsTranslationAm = lang === 'am' && (!title || title === movie.title_en);
    const needsTranslationRu = lang === 'ru' && (!title || title.includes('???'));

    if (needsTranslationAm || needsTranslationRu) {
        title = await translateText(movie.title_en || movie.title_am, lang);
        description = await translateText(movie.description_en || movie.description_am, lang);
    }

    const posterUrl = getMediaUrl(movie.poster);
    
    // Telegram Direct Range Streaming URL if telegram_message_id is set
    const streamUrl = movie.telegram_message_id ? getStreamUrl(movie.id) : null;

    // Pass the manual link directly as provided by the admin (if not empty)
    const dbVideoUrl = movie.video_url && movie.video_url.trim() !== '' 
        ? getMediaUrl(movie.video_url) 
        : null;

    return (
        <main className="min-h-screen bg-[#09090b] text-gray-200">
            {/* Cinematic Hero Section */}
            <div className="relative w-full h-[60vh] md:h-[80vh] overflow-hidden">
                <div 
                    className="absolute inset-0 bg-cover bg-center blur-xl opacity-20 scale-110" 
                    style={{ backgroundImage: `url(${posterUrl})` }} 
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[#09090b] via-[#09090b]/80 to-transparent" />
                
                <div className="absolute inset-0 max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-end md:items-center justify-start gap-12 pb-12 md:pb-0">
                    {/* Poster */}
                    <div className="w-56 md:w-80 flex-shrink-0 rounded-2xl overflow-hidden shadow-[0_0_50px_rgba(37,99,235,0.25)] border border-gray-800 hidden md:block group">
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img src={posterUrl} alt={title} className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105" />
                    </div>

                    {/* Movie Info */}
                    <div className="flex flex-col gap-5 max-w-3xl z-10 relative">
                        <Link href="/movies" className="text-gray-400 hover:text-red-500 transition-colors flex items-center gap-2 w-fit mb-2 group">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="transition-transform group-hover:-translate-x-1">
                                <line x1="19" y1="12" x2="5" y2="12"></line>
                                <polyline points="12 19 5 12 12 5"></polyline>
                            </svg>
                            {lang === 'am' ? 'Վերադառնալ' : lang === 'ru' ? 'Назад' : 'Back to Movies'}
                        </Link>
                        
                        <h1 className="text-4xl md:text-6xl font-black text-white drop-shadow-[0_0_15px_rgba(220,38,38,0.5)]">
                            {title}
                        </h1>

                        <div className="flex flex-wrap items-center gap-4 text-sm md:text-base font-medium mt-2">
                            <span className="bg-red-600 text-white px-4 py-1.5 rounded-md shadow-[0_0_15px_rgba(220,38,38,0.4)]">
                                {movie.release_year}
                            </span>
                            <span className="bg-gradient-to-r from-blue-600 to-blue-800 text-white px-4 py-1.5 rounded-md shadow-[0_0_15px_rgba(37,99,235,0.4)] border border-blue-500/30">
                                {movie.duration} {lang === 'am' ? 'րոպե' : lang === 'ru' ? 'мин.' : 'min'}
                            </span>
                            <span className="flex items-center gap-2 text-gray-300 border border-gray-700 px-4 py-1.5 rounded-md bg-gray-900/60 backdrop-blur-sm">
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-blue-400">
                                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                                    <circle cx="12" cy="12" r="3"></circle>
                                </svg>
                                {movie.views_count}
                            </span>
                        </div>

                        <p className="text-gray-300 text-lg md:text-xl leading-relaxed mt-4 border-l-4 border-blue-600 pl-4 bg-gradient-to-r from-gray-900/80 to-transparent py-2">
                            {description}
                        </p>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-6 py-12 md:py-24">
                <h2 className="text-3xl font-bold text-white mb-8 flex items-center gap-4">
                    <span className="w-10 h-1.5 bg-gradient-to-r from-red-600 to-blue-600 rounded-full shadow-[0_0_10px_rgba(220,38,38,0.5)]"></span>
                    {lang === 'am' ? 'Դիտել Օնլայն' : lang === 'ru' ? 'Смотреть Онлайн' : 'Watch Online'}
                </h2>
                
                <div className="w-full">
                    <MoviePlayer 
                        title={title} 
                        lang={lang} 
                        dbVideoUrl={dbVideoUrl} 
                        streamUrl={streamUrl}
                        poster={posterUrl}
                    />
                </div>
            </div>
        </main>
    );
}
