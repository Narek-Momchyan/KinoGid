import React from 'react';
import { Movie, MovieListProps } from '@/types/movieType';
import MovieCard from './movieCard';


import Search from './Search';

export const Metadata: Metadata = {
  title: "KinoGid",
  description:"watch movies online for free"
  
};

export default function MovieList({ movies, lang, title }: MovieListProps) {
    const defaultTitle = lang === 'am' ? 'Բոլոր Ֆիլմերը' : lang === 'ru' ? 'Все Фильмы' : 'All Movies';

    return (
        <section className="max-w-7xl mx-auto px-6 py-12">
            <div className="flex justify-between items-center mb-8">
                <h2 className="text-3xl font-bold text-white border-l-4 border-red-600 pl-4 drop-shadow-[0_0_10px_rgba(220,38,38,0.5)]">
                    {title || defaultTitle}
                </h2>
                <Search lang={lang} />
            </div>
            
            {!movies || movies.length === 0 ? (
                <div className="text-white text-center py-20">
                    {lang === 'am' ? 'Ֆիլմեր չեն գտնվել' : lang === 'ru' ? 'Фильмы не найдены' : 'No movies found'}
                </div>
            ) : (
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                    {movies.map(movie => (
                        <MovieCard key={movie.id} movie={movie} lang={lang} />
                    ))}
                </div>
            )}
        </section>
    );
}
