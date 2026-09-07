"use client";

import React, { useEffect } from 'react';
import useEmblaCarousel from 'embla-carousel-react';
import Autoplay from 'embla-carousel-autoplay';
import { HomePageMovie } from '@/types/movieType';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import Image from 'next/image';

interface SliderProps {
  items: HomePageMovie[];
}

export default function Slider({ items }: SliderProps) {
  const [emblaRef, emblaApi] = useEmblaCarousel({ loop: true, align: 'center' }, [Autoplay({ delay: 5000 })]);

  useEffect(() => {
    if (emblaApi) {
      // emblaApi.on('select', () => { ... })
    }
  }, [emblaApi]);

  const scrollPrev = () => emblaApi && emblaApi.scrollPrev();
  const scrollNext = () => emblaApi && emblaApi.scrollNext();

  if (!items || items.length === 0) {
    return null;
  }

  return (
    <div className="max-w-7xl mx-auto px-6 w-full pt-8">
      <div className="relative w-full overflow-hidden rounded-3xl shadow-2xl shadow-black" ref={emblaRef}>
        <div className="flex touch-pan-y">
          {items.map((item) => (
            <div key={item.id} className="relative flex-[0_0_100%] min-w-0">
              {item.video ? (
                <video 
                  src={item.video} 
                  autoPlay 
                  muted 
                  loop 
                  className="w-full h-[50vh] md:h-[60vh] object-cover"
                />
              ) : item.images ? (
                <div className="relative w-full h-[50vh] md:h-[60vh]">
                  <Image
                    src={item.images}
                    alt="Homepage Slider Image"
                    fill
                    className="object-cover"
                    unoptimized
                  />
                </div>
              ) : null}
              
              <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent pointer-events-none" />
            </div>
          ))}
        </div>

        <button 
          onClick={scrollPrev} 
          className="absolute left-6 top-1/2 -translate-y-1/2 p-3 bg-black/50 hover:bg-black/80 text-white rounded-full backdrop-blur-md transition-all duration-300 shadow-[0_0_15px_rgba(255,255,255,0.1)] hover:scale-110 z-10 border border-white/10"
        >
          <ChevronLeft size={28} />
        </button>
        <button 
          onClick={scrollNext} 
          className="absolute right-6 top-1/2 -translate-y-1/2 p-3 bg-black/50 hover:bg-black/80 text-white rounded-full backdrop-blur-md transition-all duration-300 shadow-[0_0_15px_rgba(255,255,255,0.1)] hover:scale-110 z-10 border border-white/10"
        >
          <ChevronRight size={28} />
        </button>
      </div>
    </div>
  );
}
