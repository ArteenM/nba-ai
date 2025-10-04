'use client';

import { useState, useEffect } from 'react';
import { useAppStore } from '@/store/appStore';
import { getGamesForDate, formatDateForDisplay } from '@/lib/dataSource';
import { Game } from '@/types';
import GameCard from '@/components/GameCard';
import Header from '@/components/Header';

export default function Dashboard() {
  const { selectedDate } = useAppStore();
  const [games, setGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadGames = async () => {
      if (!selectedDate) return;
      
      setLoading(true);
      setError(null);
      
      try {
        const gamesData = await getGamesForDate(selectedDate);
        setGames(gamesData);
      } catch (err) {
        setError('Failed to load games');
        console.error('Error loading games:', err);
      } finally {
        setLoading(false);
      }
    };

    loadGames();
  }, [selectedDate]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-900 mb-8">
              {selectedDate ? formatDateForDisplay(selectedDate) : 'Loading...'}
            </h1>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="bg-white rounded-lg shadow-md border border-gray-200 p-6 animate-pulse">
                  <div className="h-4 bg-gray-200 rounded mb-4"></div>
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-16 h-16 bg-gray-200 rounded-full"></div>
                    <div className="w-8 h-4 bg-gray-200 rounded"></div>
                    <div className="w-16 h-16 bg-gray-200 rounded-full"></div>
                  </div>
                  <div className="space-y-2">
                    <div className="h-3 bg-gray-200 rounded"></div>
                    <div className="h-3 bg-gray-200 rounded w-3/4"></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-900 mb-8">
              {selectedDate ? formatDateForDisplay(selectedDate) : 'Games'}
            </h1>
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <p className="text-red-800">{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            {selectedDate ? formatDateForDisplay(selectedDate) : 'Games'}
          </h1>
        </div>

        {games.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-gray-500 text-lg">
              No games scheduled for this date
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {games.map((game) => (
              <GameCard key={game.gameId} game={game} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}