;
import { Home } from 'lucide-react';
import Link from 'next/link';
import React from 'react'

export default function NotFound() {
  return (
    <div className='w-full flex items-center justify-center h-screen'>
      <div className='flex flex-col items-center justify-center gap-4 text-white'>
        <h1 className='text-4xl font-bold'>404</h1>
        <p className='text-lg'>Page Not Found</p>
        <Link href="/">
            <Home className='w-6 h-6  mr-2 mt-3 ' />
            Back to Home
        
        </Link>
      </div>
    </div>
  )
}   
