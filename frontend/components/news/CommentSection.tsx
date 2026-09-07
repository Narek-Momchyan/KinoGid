"use client";
import { useState } from 'react';
import { NewsComment, CommentSectionProps } from '@/types/newsType';
import { postNewsComment } from '@/lib/api';

const translations = {
    am: {
        commentsTitle: "\u0544\u0565\u056f\u0576\u0561\u0562\u0561\u0576\u0578\u0582\u0569\u0575\u0578\u0582\u0576\u0576\u0565\u0580",
        nameLabel: "\u0541\u0565\u0580 \u0561\u0576\u0578\u0582\u0576\u0568",
        namePlaceholder: "\u0555\u0580\u056b\u0576\u0561\u056f\u0589 \u0531\u0580\u0561\u0574",
        commentLabel: "\u0544\u0565\u056f\u0576\u0561\u0562\u0561\u0576\u0578\u0582\u0569\u0575\u0578\u0582\u0576",
        commentPlaceholder: "Գրեք ձեր կարծիքը...",
        submit: "\u0548\u0582\u0572\u0561\u0580\u056f\u0565\u056c",
        submitting: "\u0548\u0582\u0572\u0561\u0580\u056f\u057e\u0578\u0582\u0574 \u0567...",
        noComments: "\u0534\u0565\u057c\u0587\u057d \u0574\u0565\u056f\u0576\u0561\u0562\u0561\u0576\u0578\u0582\u0569\u0575\u0578\u0582\u0576\u0576\u0565\u0580 \u0579\u056f\u0561\u0576\u0589 \u0535\u0572\u0565\u0584 \u0561\u057c\u0561\u057b\u056b\u0576\u0568\u0589",
        errorAlert: "\u0544\u0565\u056f\u0576\u0561\u0562\u0561\u0576\u0578\u0582\u0569\u0575\u0578\u0582\u0576\u0568 \u0579\u0570\u0561\u057b\u0578\u0572\u057e\u0565\u0581 \u057a\u0561\u0570\u057a\u0561\u0576\u0565\u056c\u0589 \u053d\u0576\u0564\u0580\u0578\u0582\u0574 \u0565\u0576\u0584 \u0583\u0578\u0580\u0571\u0565\u056c \u056f\u0580\u056f\u056b\u0576\u0589",
    },
    ru: {
        commentsTitle: "\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0438",
        nameLabel: "\u0412\u0430\u0448\u0435 \u0438\u043c\u044f",
        namePlaceholder: "\u041d\u0430\u043f\u0440\u0438\u043c\u0435\u0440: \u0410\u0440\u0430\u043c",
        commentLabel: "\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0439",
        commentPlaceholder: "Напишите ваш отзыв...",
        submit: "\u041e\u0442\u043f\u0440\u0430\u0432\u0438\u0442\u044c",
        submitting: "\u041e\u0442\u043f\u0440\u0430\u0432\u043a\u0430...",
        noComments: "\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0435\u0432 \u043f\u043e\u043a\u0430 \u043d\u0435\u0442. \u0411\u0443\u0434\u044c\u0442\u0435 \u043f\u0435\u0440\u0432\u044b\u043c!",
        errorAlert: "\u041d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u0441\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c \u043a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0439. \u041f\u043e\u043f\u0440\u043e\u0431\u0443\u0439\u0442\u0435 \u0441\u043d\u043e\u0432\u0430.",
    },
    en: {
        commentsTitle: "Comments",
        nameLabel: "Your Name",
        namePlaceholder: "e.g. John",
        commentLabel: "Comment",
        commentPlaceholder: "Write your comment...",
        submit: "Submit",
        submitting: "Submitting...",
        noComments: "No comments yet. Be the first!",
        errorAlert: "Failed to save comment. Please try again.",
    }
};



export default function CommentSection({ newsId, initialComments, lang = 'am' }: CommentSectionProps) {
    const t = translations[lang as keyof typeof translations] || translations.en;
    const [comments, setComments] = useState<NewsComment[]>(initialComments);
    const [name, setName] = useState('');
    const [text, setText] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        
        if (!name.trim() || !text.trim()) return;
        
        setIsSubmitting(true);
        
        // Optimistic UI update
        const tempComment: NewsComment = {
            id: Date.now(),
            author_name: name.trim(),
            text: text.trim(),
            created_at: new Date().toISOString()
        };
        
        setComments(prev => [tempComment, ...prev]);
        setName('');
        setText('');
        
        const savedComment = await postNewsComment(newsId, tempComment.author_name, tempComment.text);
        
        if (savedComment) {
            setComments(prev => prev.map(c => c.id === tempComment.id ? savedComment : c));
        } else {
            setComments(prev => prev.filter(c => c.id !== tempComment.id));
            alert(t.errorAlert);
        }
        
        setIsSubmitting(false);
    };

    const dateLocale = lang === 'am' ? 'hy-AM' : lang === 'ru' ? 'ru-RU' : 'en-US';

    return (
        <div className="mt-12 pt-8 border-t border-gray-800">
            <h3 className="text-2xl font-bold text-white mb-6">{t.commentsTitle} ({comments.length})</h3>
            
            {/* Comment Form (Glassmorphism) */}
            <form onSubmit={handleSubmit} className="bg-[#1a1d24]/80 backdrop-blur-xl border border-gray-700/50 rounded-2xl p-6 mb-10 shadow-lg">
                <div className="mb-4">
                    <label htmlFor="comment-name" className="block text-sm font-medium text-gray-300 mb-2">{t.nameLabel}</label>
                    <input 
                        type="text" 
                        id="comment-name"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        className="w-full bg-gray-900/50 border border-gray-700 text-white rounded-lg px-4 py-3 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
                        placeholder={t.namePlaceholder}
                        required
                        disabled={isSubmitting}
                    />
                </div>
                
                <div className="mb-4">
                    <label htmlFor="comment-text" className="block text-sm font-medium text-gray-300 mb-2">{t.commentLabel}</label>
                    <textarea 
                        id="comment-text"
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                        rows={3}
                        className="w-full bg-gray-900/50 border border-gray-700 text-white rounded-lg px-4 py-3 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors resize-none"
                        placeholder={t.commentPlaceholder}
                        required
                        disabled={isSubmitting}
                    ></textarea>
                </div>
                
                <button 
                    type="submit" 
                    disabled={isSubmitting || !name.trim() || !text.trim()}
                    className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                >
                    {isSubmitting ? (
                        <>
                            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            {t.submitting}
                        </>
                    ) : t.submit}
                </button>
            </form>
            
            {/* Comments List */}
            <div className="space-y-6">
                {comments.length === 0 ? (
                    <p className="text-gray-500 italic">{t.noComments}</p>
                ) : (
                    comments.map(comment => (
                        <div key={comment.id} className="bg-gray-800/30 rounded-xl p-5 border border-gray-800 hover:border-gray-700 transition-colors">
                            <div className="flex justify-between items-start mb-2">
                                <h4 className="font-bold text-gray-200 flex items-center">
                                    <span className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-sm font-bold mr-3">
                                        {comment.author_name.charAt(0).toUpperCase()}
                                    </span>
                                    {comment.author_name}
                                </h4>
                                <span className="text-xs text-gray-500">
                                    {new Date(comment.created_at).toLocaleString(dateLocale)}
                                </span>
                            </div>
                            <p className="text-gray-300 whitespace-pre-wrap ml-11">{comment.text}</p>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
