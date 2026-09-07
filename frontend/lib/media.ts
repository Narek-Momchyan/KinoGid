export function getBaseUrl(): string {
    if (process.env.NEXT_PUBLIC_API_URL) {
        return process.env.NEXT_PUBLIC_API_URL.replace(/\/+$/, '');
    }
    if (process.env.BASE_URL) {
        return process.env.BASE_URL.replace(/\/api\/?$/, '');
    }
    return '';
}

export function getStreamUrl(movieId: number | undefined | null): string | null {
    if (!movieId) return null;
    const baseUrl = getBaseUrl();
    return `${baseUrl}/api/stream/${movieId}/`;
}

export function getMediaUrl(path: string | undefined): string {
    if (!path) return '';
    if (path.startsWith('http')) return path;
    
    const baseUrl = getBaseUrl();
    const cleanPath = path.startsWith('/') ? path.slice(1) : path;
    if (cleanPath.startsWith('media/')) {
        return `${baseUrl}/${cleanPath}`;
    }
    return `${baseUrl}/media/${cleanPath}`;
}

