import { HeaderData, LogoData, NavbarItem, LanguageItem } from '@/types/headerType';

export async function getHeaderData(lang: string = 'en'): Promise<HeaderData> {
    const [logoRes, navbarRes, langRes] = await Promise.all([
        fetch(`${process.env.BASE_URL}/header/logos/?lang=${lang}`),
        fetch(`${process.env.BASE_URL}/header/navbars/?lang=${lang}`),
        fetch(`${process.env.BASE_URL}/header/languages/?lang=${lang}`)
    ]);

    if (!logoRes.ok || !navbarRes.ok || !langRes.ok) {
        throw new Error('Failed to fetch header data');
    }

    const allLogos: LogoData[] = await logoRes.json();
    const allNavbars: NavbarItem[] = await navbarRes.json();
    const languages: LanguageItem[] = await langRes.json();

    const logo = allLogos.find(l => l.lang === lang) || (allLogos.length > 0 ? allLogos[0] : undefined);
    const navbars = allNavbars.filter(n => n.lang === lang);

    return {
        logo,
        navbar: navbars.length > 0 ? navbars : allNavbars,
        languages
    };
}

import { Movie, PaginatedMovies, HomePageMovie } from '@/types/movieType';

export async function getMovies(page: number = 1, categorySlug?: string, search?: string): Promise<PaginatedMovies> {
    try {
        let url = `${process.env.BASE_URL}/movies/?page=${page}`;
        if (categorySlug) {
            url += `&category_slug=${categorySlug}`;
        }
        if (search) {
            url += `&search=${encodeURIComponent(search)}`;
        }
        const res = await fetch(url, {
            cache: 'no-store'
        });
        if (!res.ok) return { count: 0, total_pages: 0, next: null, previous: null, results: [] };
        return res.json();
    } catch (e) {
        console.error("Error fetching movies:", e);
        return { count: 0, total_pages: 0, next: null, previous: null, results: [] };
    }
}

export async function getHomePageMovies(): Promise<HomePageMovie[]> {
    try {
        const res = await fetch(`${process.env.BASE_URL}/homepage-movies/`, {
            cache: 'no-store'
        });
        if (!res.ok) return [];
        return res.json();
    } catch (e) {
        console.error("Error fetching homepage movies:", e);
        return [];
    }
}

export async function getMovieBySlug(slug: string): Promise<Movie | null> {
    try {
      
        let res = await fetch(`${process.env.BASE_URL}/movies/${slug}/`, { cache: 'no-store' });
        if (res.ok) return res.json();

       
        res = await fetch(`${process.env.BASE_URL}/movies/`, { cache: 'no-store' });
        if (res.ok) {
            const data: PaginatedMovies = await res.json();
            return data.results.find(m => m.slug === slug) || null;
        }
        return null;
    } catch (e) {
        console.error("Error fetching movie by slug:", e);
        return null;
    }
}

export async function getSeriesEpisodes(tmdbId: number): Promise<Movie[]> {
    try {
        const res = await fetch(`${process.env.BASE_URL}/movies/?tmdb_id=${tmdbId}&is_series=true`, {
            cache: 'no-store'
        });
        if (!res.ok) return [];
        const data: PaginatedMovies = await res.json();
        
        // Sort episodes by season, then by episode number
        return data.results.sort((a, b) => {
            const seasonA = a.season_number || 0;
            const seasonB = b.season_number || 0;
            if (seasonA !== seasonB) return seasonA - seasonB;
            
            const epA = a.episode_number || 0;
            const epB = b.episode_number || 0;
            return epA - epB;
        });
    } catch (e) {
        console.error("Error fetching series episodes:", e);
        return [];
    }
}

import { NewsPost, NewsComment } from '@/types/newsType';

export async function getNews(): Promise<NewsPost[]> {
    try {
        const res = await fetch(`${process.env.BASE_URL}/news/`, {
            cache: 'no-store'
        });
        if (!res.ok) return [];
        return res.json();
    } catch (e) {
        console.error("Error fetching news:", e);
        return [];
    }
}

export async function getNewsById(id: string): Promise<NewsPost | null> {
    try {
        const res = await fetch(`${process.env.BASE_URL}/news/${id}/`, {
            cache: 'no-store'
        });
        if (!res.ok) return null;
        return res.json();
    } catch (e) {
        console.error(`Error fetching news ${id}:`, e);
        return null;
    }
}

export async function postNewsComment(newsId: number, authorName: string, text: string): Promise<NewsComment | null> {
    try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:8000/api'}/news/${newsId}/comment/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                author_name: authorName,
                text: text
            })
        });
        if (!res.ok) {
            console.error('Failed to post comment', await res.text());
            return null;
        }
        return res.json();
    } catch (e) {
        console.error("Error posting news comment:", e);
        return null;
    }
}
