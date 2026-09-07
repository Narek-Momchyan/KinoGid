import React from 'react';
import { getMovies, getHeaderData } from '@/lib/api';
import { getLang } from '@/lib/lang';
import MovieList from '@/components/movies';
import Pagination from '@/components/movies/Pagination';
import { notFound } from 'next/navigation';

interface CategoryPageProps {
    params: Promise<{ slug: string }>;
}

export default async function CategoryPage({ 
    params,
    searchParams 
}: { 
    params: Promise<{ slug: string }>;
    searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}) {
    const { slug } = await params;
    const resolvedSearchParams = await searchParams;
    const pageStr = typeof resolvedSearchParams.page === 'string' ? resolvedSearchParams.page : '1';
    const page = parseInt(pageStr, 10) || 1;
    const searchStr = typeof resolvedSearchParams.search === 'string' ? resolvedSearchParams.search : undefined;
    const lang = await getLang();
    
    // Fetch movies from backend filtered by category slug
    const moviesData = await getMovies(page, slug, searchStr);
    const categoryMovies = moviesData.results;

    // Get the category name for the title
    const headerData = await getHeaderData(lang);
    let categoryName = '';
    headerData.navbar.forEach(nav => {
        if (nav.items && Array.isArray(nav.items)) {
            const found = nav.items.find(item => item.slug === slug || item.href === `/category/${slug}`);
            if (found) categoryName = found.name;
        }
    });

    if (!categoryName) {
        // Fallback if not found in navbar, try to get from a movie
        const movieWithCat = categoryMovies.find(m => m.categories.some(c => c.slug === slug));
        if (movieWithCat) {
            const cat = movieWithCat.categories.find(c => c.slug === slug);
            if (cat) categoryName = cat.name;
        }
    }

    if (categoryMovies.length === 0) {
        return (
            <main className="min-h-[70vh] bg-[#09090b] flex flex-col items-center justify-center text-center px-4">
                <div className="w-24 h-24 mb-6 rounded-full bg-gray-800 flex items-center justify-center shadow-[0_0_30px_rgba(220,38,38,0.3)]">
                    <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-gray-400">
                        <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon>
                    </svg>
                </div>
                {categoryName && (
                    <h1 className="text-3xl font-bold text-white mb-6">
                        {categoryName}
                    </h1>
                )}
                
                <div className="space-y-3 bg-gray-900/50 p-8 rounded-2xl border border-gray-800 backdrop-blur-sm max-w-lg">
                    <p className="text-red-500 font-medium text-lg">
                        {lang === 'am' ? 'Այս ժանրի ֆիլմ այս պահին չկա' : 
                         lang === 'ru' ? 'В данный момент фильмов этого жанра нет' : 
                         'There are currently no movies in this genre'}
                    </p>
                    <p className="text-gray-500 text-sm">
                        {lang === 'am' ? 'Խնդրում ենք ստուգել ավելի ուշ կամ ընտրել այլ ժանր:' : 
                         lang === 'ru' ? 'Пожалуйста, проверьте позже или выберите другой жанр.' : 
                         'Please check back later or select another genre.'}
                    </p>
                </div>
            </main>
        );
    }

    return (
        <main className="min-h-screen bg-[#09090b]">
            <MovieList 
                movies={categoryMovies} 
                lang={lang} 
                title={categoryName || (lang === 'am' ? 'Ֆիլմեր' : lang === 'ru' ? 'Фильмы' : 'Movies')}
            />
            <Pagination 
                currentPage={page} 
                totalPages={moviesData.total_pages} 
                basePath={`/category/${slug}`} 
            />
        </main>
    );
}
