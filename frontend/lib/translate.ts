export async function translateText(text: string, targetLang: string): Promise<string> {
    if (!text || targetLang === 'en') return text;
    
    const tl = targetLang === 'am' ? 'hy' : targetLang;
    
    try {
        const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=${tl}&dt=t&q=${encodeURIComponent(text)}`;
        const res = await fetch(url, { cache: 'force-cache' });
        if (!res.ok) return text;
        const data = await res.json();
     
        return data[0].map((x: any) => x[0]).join('');
    } catch (e) {
        console.error("Translation error", e);
        return text;
    }
}
