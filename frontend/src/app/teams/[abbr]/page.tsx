'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { getTeamByAbbreviation, getTeamSchedule } from '@/lib/dataSource';
import { Team, Game } from '@/types';
import Header from '@/components/Header';

export default function TeamDetailsPage() {
  const params = useParams();
  const teamAbbr = params.abbr as string;
  
  const [team, setTeam] = useState<Team | null>(null);
  const [games, setGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(true);
  const [aiLoading, setAiLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadTeamData = async () => {
      if (!teamAbbr) return;
      
      setLoading(true);
      setError(null);
      
      try {
        // First load team info
        const teamData = await getTeamByAbbreviation(teamAbbr);
        if (!teamData) {
          setError('Team not found');
          return;
        }
        setTeam(teamData);

        // Simulate AI processing time
        setAiLoading(true);
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Then load team schedule
        const scheduleData = await getTeamSchedule(teamAbbr);
        setGames(scheduleData);
      } catch (err) {
        setError('Failed to load team data');
        console.error('Error loading team data:', err);
      } finally {
        setLoading(false);
        setAiLoading(false);
      }
    };

    loadTeamData();
  }, [teamAbbr]);

  const formatGameTime = (dateTimeUTC: string) => {
    const date = new Date(dateTimeUTC);
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  };

  const formatGameDate = (dateTimeUTC: string) => {
    const date = new Date(dateTimeUTC);
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
    });
  };

  const getOpponent = (game: Game) => {
    return game.homeTeam.teamTricode === teamAbbr ? game.awayTeam : game.homeTeam;
  };

  const isHomeGame = (game: Game) => {
    return game.homeTeam.teamTricode === teamAbbr;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/4 mb-8"></div>
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-16 bg-gray-200 rounded"></div>
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
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <p className="text-red-800">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!team) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900">Team not found</h1>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      {/* AI Loading Overlay */}
      {aiLoading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md mx-4 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              AI Analysis in Progress
            </h3>
            <p className="text-gray-600">
              Our AI model is analyzing team performance and generating predictions...
            </p>
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Team Header */}
        <div className="bg-white rounded-lg shadow-md border border-gray-200 p-8 mb-8">
          <div className="flex items-center">
            <div className="w-24 h-24 mr-6 flex items-center justify-center">
              <img
                src={team.teamLogo}
                alt={`${team.teamName} logo`}
                className="w-full h-full object-contain"
                onError={(e) => {
                  const target = e.target as HTMLImageElement;
                  target.style.display = 'none';
                  const parent = target.parentElement;
                  if (parent) {
                    parent.innerHTML = `<div class="w-24 h-24 bg-gray-200 rounded-full flex items-center justify-center text-2xl font-bold text-gray-600">${team.teamTricode}</div>`;
                  }
                }}
              />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {team.teamCity} {team.teamName}
              </h1>
              <p className="text-lg text-gray-600 mt-1">
                {team.teamConference && team.teamDivision ? `${team.teamConference} • ${team.teamDivision}` : `Record: ${team.wins}-${team.losses}`}
              </p>
            </div>
          </div>
        </div>

        {/* Upcoming Games */}
        <div className="bg-white rounded-lg shadow-md border border-gray-200 p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Upcoming Games</h2>
          
          {games.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-500">No games found for this team</p>
            </div>
          ) : (
            <div className="space-y-4">
              {games.slice(0, 10).map((game) => {
                const opponent = getOpponent(game);
                const homeGame = isHomeGame(game);
                
                return (
                  <div
                    key={game.gameId}
                    className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-center space-x-4">
                      <div className="text-sm text-gray-500 w-20">
                        {formatGameDate(game.gameDateTimeUTC)}
                      </div>
                      <div className="text-sm text-gray-500 w-20">
                        {formatGameTime(game.gameDateTimeUTC)}
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="w-8 h-8 flex items-center justify-center">
                          <img
                            src={opponent.teamLogo}
                            alt={`${opponent.teamName} logo`}
                            className="w-full h-full object-contain"
                            onError={(e) => {
                              const target = e.target as HTMLImageElement;
                              target.style.display = 'none';
                              const parent = target.parentElement;
                              if (parent) {
                                parent.innerHTML = `<div class="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center text-xs font-bold text-gray-600">${opponent.teamTricode}</div>`;
                              }
                            }}
                          />
                        </div>
                        <span className="font-medium text-gray-900">
                          {opponent.teamCity} {opponent.teamName}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        homeGame 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-blue-100 text-blue-800'
                      }`}>
                        {homeGame ? 'Home' : 'Away'}
                      </span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        game.gameStatus === 1 
                          ? 'bg-yellow-100 text-yellow-800'
                          : game.gameStatus === 2
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {game.gameStatus === 1 ? 'Scheduled' : game.gameStatus === 2 ? 'Live' : 'Final'}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
