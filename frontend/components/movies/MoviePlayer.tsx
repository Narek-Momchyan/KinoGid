'use client';

import React from 'react';
import dynamic from 'next/dynamic';
import Link from 'next/link';
import { getMediaUrl } from '@/lib/media';
import 'plyr-react/plyr.css';

// Load Plyr dynamically to avoid SSR issues and use the named export
const Plyr = dynamic(() => import('plyr-react').then((mod) => mod.Plyr), { ssr: false });

interface MoviePlayerProps {
    title: string;
    lang: string;
    dbVideoUrl?: string | null;
    streamUrl?: string | null;
    poster?: string | null;
    episodes?: any[];
    currentMovie?: any;
}

export default function MoviePlayer({ title, lang, dbVideoUrl, streamUrl, poster, episodes, currentMovie }: MoviePlayerProps) {
    const plyrRef = React.useRef<any>(null);

    const plyrSource = React.useMemo(() => {
        if (!streamUrl) return null;
        return {
            type: 'video' as const,
            title: title,
            sources: [
                {
                    src: streamUrl,
                    type: 'video/mp4',
                }
            ],
            poster: poster || undefined,
        };
    }, [streamUrl, title, poster]);

    const plyrOptions = React.useMemo(() => {
        return {
            controls: [
                'play-large', 'rewind', 'play', 'fast-forward', 'progress', 'current-time', 
                'duration', 'mute', 'volume', 'captions', 'settings', 
                'pip', 'airplay', 'fullscreen'
            ],
            settings: ['captions', 'quality', 'speed'],
            seekTime: 10,
            keyboard: { focused: true, global: true },
        };
    }, []);

    const handleDoubleClick = (e: React.MouseEvent<HTMLDivElement>) => {
        const player = plyrRef.current?.plyr;
        if (!player) return;

        const rect = e.currentTarget.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const width = rect.width;

        // Եթե սեղմել է էկրանի աջ կեսում, առաջ ենք տալիս 10 վայրկյան
        if (clickX > width / 2) {
            player.forward(10);
        } else {
            // Եթե ձախ կեսում է, հետ ենք տալիս 10 վայրկյան
            player.rewind(10);
        }
    };

    return (
        <div className="flex flex-col gap-6">
            {streamUrl && plyrSource ? (
                <div 
                    className="relative w-full aspect-video bg-black rounded-2xl overflow-hidden shadow-2xl border border-gray-800 plyr-custom-container"
                    onDoubleClick={handleDoubleClick}
                >
                    <Plyr
                        ref={plyrRef}
                        source={plyrSource as any}
                        options={plyrOptions}
                    />
                    <style jsx global>{`
                        .plyr-custom-container {
                            --plyr-color-main: #e50914;
                        }
                        .plyr-custom-container .plyr {
                            height: 100%;
                            width: 100%;
                        }
                    `}</style>
                </div>
            ) : dbVideoUrl ? (
                <div className="relative w-full aspect-video bg-[#09090b] rounded-2xl overflow-hidden border border-gray-800 shadow-2xl">
                    <iframe
                        src={dbVideoUrl}
                        width="100%"
                        height="100%"
                        allowFullScreen
                        frameBorder="0"
                        title={title}
                        className="w-full h-full border-0"
                    ></iframe>
                </div>
            ) : (
                <div className="relative w-full aspect-video bg-[#09090b] rounded-2xl overflow-hidden flex flex-col items-center justify-center text-gray-400 border border-gray-800">
                    <span className="text-xl md:text-2xl text-center px-4">
                        🎬 {lang === 'am' ? 'Ֆիլմը շուտով կհրապարակվի' : lang === 'ru' ? 'Фильм скоро появится' : 'The movie will be published soon'}
                    </span>
                </div>
            )}

            {/* Episodes List */}
            {episodes && episodes.length > 0 && (
                <div className="bg-gray-900/50 p-6 rounded-2xl border border-gray-800 backdrop-blur-sm mt-4">
                    <h3 className="text-2xl font-bold text-white mb-6">
                        {lang === 'am' ? 'Սերիաներ' : lang === 'ru' ? 'Серии' : 'Episodes'}
                    </h3>
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
                        {episodes.map((ep) => {
                            const isCurrent = currentMovie?.id === ep.id;
                            return (
                                <Link 
                                    href={`/movies/${ep.slug}`} 
                                    key={ep.id}
                                    className={`relative group overflow-hidden rounded-xl border ${isCurrent ? 'border-red-500 bg-red-500/10' : 'border-gray-700 bg-gray-800/50 hover:border-gray-500'} transition-all duration-300 flex flex-col`}
                                >
                                    <div className="aspect-video w-full bg-gray-900 flex items-center justify-center overflow-hidden">
                                        {/* eslint-disable-next-line @next/next/no-img-element */}
                                        {ep.poster ? (
                                            <img 
                                                src={getMediaUrl(ep.poster)} 
                                                alt={ep.title_en || 'Episode'} 
                                                className="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity" 
                                            />
                                        ) : (
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-gray-600"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                                        )}
                                        {isCurrent && (
                                            <div className="absolute inset-0 flex items-center justify-center bg-black/40">
                                                <div className="bg-red-600 text-white text-xs font-bold px-2 py-1 rounded animate-pulse">
                                                    {lang === 'am' ? 'Դիտում եք' : lang === 'ru' ? 'Смотрите' : 'Playing'}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                    <div className="p-3 text-center">
                                        <div className="text-xs text-gray-400 mb-1">
                                            {lang === 'am' ? 'Եթերաշրջան' : lang === 'ru' ? 'Сезон' : 'Season'} {ep.season_number || 1}
                                        </div>
                                        <div className="font-bold text-gray-200 group-hover:text-white transition-colors">
                                            {lang === 'am' ? 'Սերիա' : lang === 'ru' ? 'Серия' : 'Episode'} {ep.episode_number || 1}
                                        </div>
                                    </div>
                                </Link>
                            );
                        })}
                    </div>
                </div>
            )}
        </div>
    );
}

