'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { getAllTeams } from '@/lib/dataSource';
import { Team } from '@/types';
import Header from '@/components/Header';

export default function TeamsPage() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadTeams = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const teamsData = await getAllTeams();
        // Sort teams alphabetically by city name
        const sortedTeams = teamsData.sort((a, b) => a.teamCity.localeCompare(b.teamCity));
        setTeams(sortedTeams);
      } catch (err) {
        setError('Failed to load teams');
        console.error('Error loading teams:', err);
      } finally {
        setLoading(false);
      }
    };

    loadTeams();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">NBA Teams</h1>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {[...Array(30)].map((_, i) => (
              <div key={i} className="bg-white rounded-lg shadow-md border border-gray-200 p-6 animate-pulse">
                <div className="w-20 h-20 bg-gray-200 rounded-full mx-auto mb-4"></div>
                <div className="h-4 bg-gray-200 rounded mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-3/4 mx-auto"></div>
              </div>
            ))}
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
          <h1 className="text-3xl font-bold text-gray-900 mb-8">NBA Teams</h1>
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <p className="text-red-800">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">NBA Teams</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {teams.map((team) => (
            <Link
              key={team.teamId}
              href={`/teams/${team.teamTricode}`}
              className="bg-white rounded-lg shadow-md border border-gray-200 p-6 hover:shadow-lg transition-shadow duration-200 group"
            >
              <div className="text-center">
                <div className="w-20 h-20 mx-auto mb-4 flex items-center justify-center">
                  <img
                    src={team.teamLogo}
                    alt={`${team.teamName} logo`}
                    className="w-full h-full object-contain"
                    onError={(e) => {
                      // Fallback to team abbreviation if logo fails to load
                      const target = e.target as HTMLImageElement;
                      target.style.display = 'none';
                      const parent = target.parentElement;
                      if (parent) {
                        parent.innerHTML = `<div class="w-20 h-20 bg-gray-200 rounded-full flex items-center justify-center text-lg font-bold text-gray-600">${team.teamTricode}</div>`;
                      }
                    }}
                  />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                  {team.teamCity}
                </h3>
                <p className="text-sm text-gray-600">
                  {team.teamName}
                </p>
                <div className="mt-2 text-xs text-gray-500">
                  {team.teamConference && team.teamDivision ? `${team.teamConference} • ${team.teamDivision}` : `Record: ${team.wins}-${team.losses}`}
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
