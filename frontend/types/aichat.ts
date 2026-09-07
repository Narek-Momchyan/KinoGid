export interface RecommendedMovie {
    id: number;
    title: string;
    slug: string;
    poster: string | null;
    release_year: number;
}

export interface ChatMessage {
    role: 'user' | 'ai';
    text: string;
    movies?: RecommendedMovie[];
}

export interface AIChatProps {
    lang: 'am' | 'ru' | 'en';
}