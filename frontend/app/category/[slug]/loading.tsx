import React from 'react';

export default function Loading() {
    return (
        <main className="min-h-screen bg-[#09090b]">
            <div className="max-w-7xl mx-auto px-6 pt-12 pb-4">
                <div className="flex items-center gap-4 animate-pulse">
                    <div className="w-8 h-8 rounded-lg bg-gray-800"></div>
                    <div className="w-48 h-10 bg-gray-800 rounded-lg"></div>
                </div>
                <div className="w-24 h-4 bg-gray-800 rounded mt-3 animate-pulse"></div>
            </div>
            
            <section className="max-w-7xl mx-auto px-6 py-12">
                <div className="w-40 h-8 bg-gray-800 rounded-lg mb-8 animate-pulse border-l-4 border-gray-700"></div>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                    {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(i => (
                        <div key={i} className="group relative rounded-xl overflow-hidden shadow-lg bg-gray-900 border border-gray-800 flex flex-col animate-pulse">
                            <div className="relative aspect-[2/3] w-full bg-gray-800"></div>
                            <div className="p-4 relative flex-1 flex flex-col justify-between">
                                <div className="w-full h-5 bg-gray-800 rounded mb-3"></div>
                                <div className="w-1/3 h-4 bg-gray-800 rounded"></div>
                            </div>
                        </div>
                    ))}
                </div>
            </section>
        </main>
    );
}
