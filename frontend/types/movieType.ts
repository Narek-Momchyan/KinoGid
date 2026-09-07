export interface Actor {
    id: number;
    name_am?: string;
    name_ru?: string;
    name_en: string;
    photo?: string;
}

export interface Movie {
    id: number;
    title_am?: string;
    title_ru?: string;
    title_en?: string;
    description_am?: string;
    description_ru?: string;
    description_en?: string;
    slug: string;
    poster: string;
    video_url?: string;
    telegram_message_id?: number;
    release_year: number;
    duration: number;
    views_count: number;
    created_at: string;
    categories: any[];
    actors: Actor[];
    tmdb_id?: number;
    season_number?: number;
    episode_number?: number;
    is_series?: boolean;
}

export interface PaginatedMovies {
    count: number;
    total_pages: number;
    next: string | null;
    previous: string | null;
    results: Movie[];
}

export interface HomePageMovie {
    id: number;
    images: string | null;
    video: string | null;
}
export interface MovieListProps {
    movies: Movie[];
    lang: string;
    title?: string;
}