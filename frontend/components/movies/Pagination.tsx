import React from 'react';
import Link from 'next/link';

interface PaginationProps {
    currentPage: number;
    totalPages: number;
    basePath?: string;
}

export default function Pagination({ currentPage, totalPages, basePath = '/' }: PaginationProps) {
    if (totalPages <= 1) return null;

    const maxPagesToShow = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxPagesToShow / 2));
    let endPage = startPage + maxPagesToShow - 1;

    if (endPage > totalPages) {
        endPage = totalPages;
        startPage = Math.max(1, endPage - maxPagesToShow + 1);
    }

    const pages = Array.from({ length: endPage - startPage + 1 }, (_, i) => startPage + i);

    return (
        <div className="flex items-center justify-center space-x-2 my-8">
            {currentPage > 1 && (
                <Link
                    href={`${basePath}?page=${currentPage - 1}`}
                    className="px-4 py-2 bg-gray-800 text-white rounded-md hover:bg-gray-700 transition-colors"
                >
                    &laquo;
                </Link>
            )}

            {startPage > 1 && (
                <>
                    <Link
                        href={`${basePath}?page=1`}
                        className="px-4 py-2 bg-gray-800 text-white rounded-md hover:bg-gray-700 transition-colors"
                    >
                        1
                    </Link>
                    {startPage > 2 && <span className="text-gray-500">...</span>}
                </>
            )}

            {pages.map(page => (
                <Link
                    key={page}
                    href={`${basePath}?page=${page}`}
                    className={`px-4 py-2 rounded-md transition-colors ${
                        page === currentPage
                            ? 'bg-red-600 text-white'
                            : 'bg-gray-800 text-white hover:bg-gray-700'
                    }`}
                >
                    {page}
                </Link>
            ))}

            {endPage < totalPages && (
                <>
                    {endPage < totalPages - 1 && <span className="text-gray-500">...</span>}
                    <Link
                        href={`${basePath}?page=${totalPages}`}
                        className="px-4 py-2 bg-gray-800 text-white rounded-md hover:bg-gray-700 transition-colors"
                    >
                        {totalPages}
                    </Link>
                </>
            )}

            {currentPage < totalPages && (
                <Link
                    href={`${basePath}?page=${currentPage + 1}`}
                    className="px-4 py-2 bg-gray-800 text-white rounded-md hover:bg-gray-700 transition-colors"
                >
                    &raquo;
                </Link>
            )}
        </div>
    );
}
