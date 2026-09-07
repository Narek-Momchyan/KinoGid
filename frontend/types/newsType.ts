export interface NewsComment {
    id: number;
    author_name: string;
    text: string;
    created_at: string;
}

export interface NewsPost {
    id: number;
    title: string;
    content: string;
    image_url: string | null;
    created_at: string;
    generated_by_ai: boolean;
    comments: NewsComment[];
}
export interface CommentSectionProps {
    newsId: number;
    initialComments: NewsComment[];
    lang?: string;
}