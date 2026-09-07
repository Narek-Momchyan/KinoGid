'use client';

import React from 'react';

export default function AIChatButton() {
    const handleClick = () => {
        window.dispatchEvent(new Event('open-ai-chat'));
    };

    return (
        <button 
            onClick={handleClick}
            className="flex cursor-pointer items-center justify-center w-10 h-10 rounded-full bg-gradient-to-r from-red-600 to-blue-600 hover:scale-110 transition-transform shadow-[0_0_15px_rgba(220,38,38,0.3)] ml-4"
            aria-label="Open AI Advisor"
            title="AI Կինոգետ"
        >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-white">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                <path d="M9 10h.01"></path>
                <path d="M15 10h.01"></path>
                <path d="M12 10h.01"></path>
            </svg>
        </button>
    );
}
