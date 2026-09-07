import { getNews } from "@/lib/api";
import { getLang } from "@/lib/lang";
import Link from "next/link";

const t = {
    am: {
        title: "\u053f\u056b\u0576\u0578\u0561\u0577\u056d\u0561\u0580\u0570\u056b \u0546\u0578\u0580\u0578\u0582\u0569\u0575\u0578\u0582\u0576\u0576\u0565\u0580 (AI Blogger)",
        empty: "\u0531\u057c\u0561\u0575\u056a\u0574 \u0576\u0578\u0580\u0578\u0582\u0569\u0575\u0578\u0582\u0576\u0576\u0565\u0580 \u0579\u056f\u0561\u0576:",
    },
    ru: {
        title: "\u041d\u043e\u0432\u043e\u0441\u0442\u0438 \u043a\u0438\u043d\u043e (AI Blogger)",
        empty: "\u041d\u043e\u0432\u043e\u0441\u0442\u0435\u0439 \u043f\u043e\u043a\u0430 \u043d\u0435\u0442.",
    },
    en: {
        title: "Cinema News (AI Blogger)",
        empty: "No news available yet.",
    }
};

export default async function NewsPage() {
    const lang = await getLang();
    const news = await getNews();
    const tr = t[lang as keyof typeof t] || t.en;
    const dateLocale = lang === 'am' ? 'hy-AM' : lang === 'ru' ? 'ru-RU' : 'en-US';

    return (
        <div className="container mx-auto px-4 py-8 max-w-5xl">
            <h1 className="text-3xl font-bold mb-8 text-white">{tr.title}</h1>
            
            {news.length === 0 ? (
                <div className="text-gray-400 text-center py-10">{tr.empty}</div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {news.map((item) => (
                        <Link href={`/news/${item.id}`} key={item.id} className="block group">
                            <div className="bg-[#1a1d24]/60 backdrop-blur-md border border-gray-800 rounded-2xl overflow-hidden hover:border-gray-600 transition-all duration-300 transform group-hover:-translate-y-1 shadow-lg">
                                {item.image_url ? (
                                    <div className="h-48 w-full relative overflow-hidden bg-gray-900">
                                        {/* eslint-disable-next-line @next/next/no-img-element */}
                                        <img 
                                            src={item.image_url} 
                                            alt={item.title} 
                                            className="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity duration-300"
                                        />
                                    </div>
                                ) : (
                                    <div className="h-48 w-full bg-gradient-to-br from-gray-900 to-[#1a1d24] flex items-center justify-center text-gray-700">
                                        <svg className="w-16 h-16 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9.5a2.5 2.5 0 00-2.5-2.5H15" />
                                        </svg>
                                    </div>
                                )}
                                <div className="p-6">
                                    <h2 className="text-xl font-bold text-gray-100 mb-3 line-clamp-2 group-hover:text-white transition-colors">{item.title}</h2>
                                    <p className="text-gray-400 text-sm line-clamp-3 mb-4">
                                        {item.content}
                                    </p>
                                    <div className="flex justify-between items-center text-xs text-gray-500">
                                        <span>{new Date(item.created_at).toLocaleDateString(dateLocale)}</span>
                                        {item.generated_by_ai && (
                                            <span className="bg-blue-900/40 text-blue-400 px-2 py-1 rounded-md border border-blue-800/50 flex items-center">
                                                <svg className="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                                </svg>
                                                AI
                                            </span>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </Link>
                    ))}
                </div>
            )}
        </div>
    );
}
