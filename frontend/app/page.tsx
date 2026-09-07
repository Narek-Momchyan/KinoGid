import { getMovies, getHomePageMovies } from '@/lib/api';
import { getLang } from '@/lib/lang';
import MovieList from '@/components/movies';
import Pagination from '@/components/movies/Pagination';
import Slider from '@/components/movies/Slider';

export default async function MoviesPage({
  searchParams,
}: {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>
}) {
  const resolvedSearchParams = await searchParams;
  const pageStr = typeof resolvedSearchParams.page === 'string' ? resolvedSearchParams.page : '1';
  const page = parseInt(pageStr, 10) || 1;
  const searchStr = typeof resolvedSearchParams.search === 'string' ? resolvedSearchParams.search : undefined;
  const lang = await getLang();
  
  const moviesData = await getMovies(page, undefined, searchStr);
  const homePageMovies = await getHomePageMovies();

  return (
    <main className="min-h-screen bg-black">
      <Slider items={homePageMovies} />
      <div className="pt-8 pb-12">
        <MovieList movies={moviesData.results} lang={lang} />
        <Pagination 
           currentPage={page} 
           totalPages={moviesData.total_pages} 
           basePath="/" 
        />
      </div>
    </main>
  );
}
