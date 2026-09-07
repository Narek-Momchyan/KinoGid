'use client';

import React, { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import { getMediaUrl } from '@/lib/media';
import { Metadata } from 'next';
import { AIChatProps, ChatMessage, RecommendedMovie } from '@/types/aichat';

export const Metadata: Metadata = {
  title: "KinoGid",
  description:"watch movies online for free"
  
};
export default function AIChat({ lang }: AIChatProps) {
    const [isOpen, setIsOpen] = useState(false);
    const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
    const [inputText, setInputText] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Listen for header button click
    useEffect(() => {
        const handler = () => setIsOpen(true);
        window.addEventListener('open-ai-chat', handler);
        return () => window.removeEventListener('open-ai-chat', handler);
    }, []);

    // Auto-scroll to bottom of chat
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [chatHistory, isLoading]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        
        if (!inputText.trim()) return;

        const userMsg = inputText.trim();
        setInputText('');
        
        
        setChatHistory(prev => [...prev, { role: 'user', text: userMsg }]);
        setIsLoading(true);

        try {
            const apiUrl = `${process.env.NEXT_PUBLIC_API_URL}/api/ai_chat/`;

            const formattedHistory = chatHistory.map(msg => ({
                role: msg.role,
                text: msg.text
            }));

            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    user_message: userMsg,
                    history: formattedHistory,
                    lang: lang
                })
            });

            if (!response.ok) {
                throw new Error('API request failed');
            }

            const data = await response.json();
            
            
            const errorText1 = lang === 'en' ? 'Sorry, something went wrong while getting the response.' :
                               lang === 'ru' ? 'Извините, при получении ответа произошла ошибка.' :
                               'Կներեք, որևէ խնդիր առաջացավ պատասխանը ստանալիս։';

            setChatHistory(prev => [
                ...prev, 
                { 
                    role: 'ai', 
                    text: data.reply || errorText1,
                    movies: data.recommended_movies || []
                }
            ]);
            
        } catch (error) {
            console.error('AI Chat Error:', error);
            const errorText2 = lang === 'en' ? 'Sorry, the service is temporarily unavailable. Please try again later.' :
                               lang === 'ru' ? 'Извините, сервис временно недоступен. Пожалуйста, попробуйте позже.' :
                               'Կներեք, ծառայությունը ժամանակավորապես անհասանելի է։ Խնդրում ենք փորձել մի փոքր ուշ։';
            setChatHistory(prev => [
                ...prev, 
                { 
                    role: 'ai', 
                    text: errorText2
                }
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <>

            <div className={`fixed bottom-6 right-6 w-[350px] sm:w-96 h-[32rem] z-40 flex flex-col bg-black/95 backdrop-blur-xl border border-zinc-800 rounded-2xl shadow-[0_0_30px_rgba(0,0,0,0.8)] overflow-hidden transition-all duration-300 transform ${isOpen ? 'translate-y-0 opacity-100' : 'translate-y-12 opacity-0 pointer-events-none'}`}>
                
                <div className="flex justify-between items-center px-5 py-4 border-b border-zinc-800 bg-black/50">
                    <div className="flex items-center gap-3">
                        <div>
                            <h3 className="text-lg font-extrabold bg-gradient-to-r from-red-500 to-blue-600 bg-clip-text text-transparent pb-1">
                                {lang === 'en' ? 'AI Movie Advisor' : lang === 'ru' ? 'AI Киновед' : 'AI Կինոգետ'}
                            </h3>
                            <p className="text-zinc-400 text-xs flex items-center gap-1 mt-0.5">
                                <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></span>
                                {lang === 'en' ? 'Online' : lang === 'ru' ? 'В сети' : 'Առցանց'}
                            </p>
                        </div>
                    </div>
                    <button onClick={() => setIsOpen(false)} className="text-zinc-400 cursor-pointer hover:text-white transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                    </button>
                </div>

                {/* Chat History */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
                    {chatHistory.map((msg, idx) => (
                        <div key={idx} className={`flex flex-col w-full ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                            
                            <div className={
                                msg.role === 'user' 
                                    ? 'bg-blue-600 text-white rounded-2xl rounded-br-sm px-4 py-2.5 max-w-[80%] shadow-lg text-sm ml-auto' 
                                    : 'bg-zinc-900 border border-zinc-800 text-zinc-200 rounded-2xl rounded-bl-sm px-4 py-2.5 max-w-[90%] shadow-md text-sm leading-relaxed'
                            }>
                                {msg.text}
                                
                                {/* Recommended Movies */}
                                {msg.movies && msg.movies.length > 0 && (
                                    <div className="flex flex-col gap-2 mt-3">
                                        {msg.movies.map((movie) => (
                                            <Link 
                                                href={`/movies/${movie.slug}`} 
                                                key={movie.id}
                                                className="group flex items-center bg-black border border-zinc-800 hover:border-red-500 hover:bg-zinc-900 rounded-xl p-2 transition-all duration-300 hover:-translate-y-1 cursor-pointer"
                                            >
                                                <div className="w-10 h-14 bg-zinc-800 rounded overflow-hidden flex-shrink-0 relative">
                                                    {movie.poster ? (
                                                        <img src={getMediaUrl(movie.poster)} alt={movie.title} className="w-full h-full object-cover group-hover:opacity-75 transition-opacity" />
                                                    ) : (
                                                        <div className="w-full h-full flex items-center justify-center text-[10px] text-zinc-500">No Img</div>
                                                    )}
                                                    <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                                                        <div className="bg-red-600/80 rounded-full p-1">
                                                            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                                                        </div>
                                                    </div>
                                                </div>
                                                <div className="flex-1 min-w-0 ml-3">
                                                    <h4 className="text-sm font-semibold text-zinc-200 group-hover:text-red-400 truncate transition-colors">{movie.title}</h4>
                                                    <p className="text-zinc-500 text-xs mt-0.5">{movie.release_year}</p>
                                                </div>
                                            </Link>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                    
                    {isLoading && (
                        <div className="flex items-start">
                            <div className="bg-zinc-900 border border-zinc-800 text-zinc-400 px-4 py-3 rounded-2xl rounded-bl-sm shadow-md flex items-center gap-1.5">
                                <span className="w-1.5 h-1.5 rounded-full bg-zinc-500 animate-bounce" style={{animationDelay: '0ms'}}></span>
                                <span className="w-1.5 h-1.5 rounded-full bg-zinc-500 animate-bounce" style={{animationDelay: '150ms'}}></span>
                                <span className="w-1.5 h-1.5 rounded-full bg-zinc-500 animate-bounce" style={{animationDelay: '300ms'}}></span>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* Input Area */}
                <div className="p-4 bg-black border-t border-zinc-800 relative">
                    <form onSubmit={handleSubmit} className="relative">
                        <input 
                            type="text" 
                            value={inputText}
                            onChange={(e) => setInputText(e.target.value)}
                            placeholder={lang === 'en' ? 'What would you like to watch...' : lang === 'ru' ? 'Что бы вы хотели посмотреть...' : 'Ի՞նչ կցանկանաք դիտել...'}
                            className="w-full bg-zinc-900 border border-zinc-800 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 rounded-full pl-5 pr-12 py-3 text-zinc-100 outline-none placeholder-zinc-500 text-sm transition-all"
                            disabled={isLoading}
                        />
                        <button 
                            type="submit"
                            disabled={!inputText.trim() || isLoading}
                            className=" cursor-pointer absolute right-1.5 top-1.5 bottom-1.5 bg-red-600 hover:bg-red-500 text-white p-2 rounded-full transition-transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center justify-center aspect-square"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
                        </button>
                    </form>
                </div>
            </div>
        </>
    );
}
