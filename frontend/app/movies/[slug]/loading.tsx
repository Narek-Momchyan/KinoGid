import React from 'react';

export default function Loading() {
    return (
        <div className="min-h-screen bg-[#09090b] flex flex-col animate-pulse">
            <div className="w-full h-[60vh] md:h-[80vh] bg-gray-900/50 relative border-b border-gray-800">
                <div className="absolute inset-0 bg-gradient-to-t from-[#09090b] to-transparent" />
                <div className="absolute inset-0 max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-end md:items-center justify-start gap-12 pb-12 md:pb-0">
                    <div className="hidden md:block w-56 md:w-80 h-[330px] md:h-[480px] bg-gray-800/80 rounded-2xl shadow-xl border border-gray-700/50"></div>
                    <div className="flex flex-col gap-6 flex-1 w-full max-w-3xl relative z-10">
                        <div className="w-32 h-6 bg-gray-800/80 rounded-md"></div>
                        <div className="w-3/4 h-16 md:h-20 bg-gray-800/80 rounded-lg"></div>
                        <div className="flex gap-4">
                            <div className="w-20 h-10 bg-gray-800/80 rounded-md"></div>
                            <div className="w-28 h-10 bg-gray-800/80 rounded-md"></div>
                            <div className="w-24 h-10 bg-gray-800/80 rounded-md"></div>
                        </div>
                        <div className="w-full h-32 bg-gray-800/60 rounded-lg mt-4"></div>
                    </div>
                </div>
            </div>
            
            <div className="max-w-7xl mx-auto px-6 w-full py-12 md:py-24">
                <div className="w-48 h-10 bg-gray-800/80 rounded-md mb-8"></div>
                <div className="w-full aspect-video bg-gray-900/80 rounded-2xl border border-gray-800/80"></div>
            </div>
        </div>
    );
}
