'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { PredictionResult, Team } from '@/types';
import { predictWinner } from '@/lib/api';
import { getAllTeams } from '@/lib/dataSource';

export default function PredictionPage() {
  const params = useParams();
  const router = useRouter();
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [team1Info, setTeam1Info] = useState<Team | null>(null);
  const [team2Info, setTeam2Info] = useState<Team | null>(null);

  const team1 = params.team1 as string;
  const team2 = params.team2 as string;

  useEffect(() => {
    const fetchPrediction = async () => {
      try {
        setLoading(true);
        setError(null);

        // Get team info for logos and names
        const teams = await getAllTeams();
        const team1Data = teams.find(t => t.teamTricode === team1.toUpperCase());
        const team2Data = teams.find(t => t.teamTricode === team2.toUpperCase());

        setTeam1Info(team1Data || null);
        setTeam2Info(team2Data || null);

        // Call prediction API
        const result = await predictWinner({
          team1: team1.toUpperCase(),
          team2: team2.toUpperCase(),
        });

        setPrediction(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to get prediction');
      } finally {
        setLoading(false);
      }
    };

    fetchPrediction();
  }, [team1, team2]);

  const StatCard = ({ label, team1Value, team2Value }: {
    label: string;
    team1Value: number;
    team2Value: number;
  }) => {
    const team1Wins = team1Value > team2Value;
    const team2Wins = team2Value > team1Value;

    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="text-sm font-medium text-gray-600 mb-3">{label}</div>
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-700">{team1}</span>
            <span className={`font-medium ${team1Wins ? 'text-green-600' : 'text-gray-900'}`}>
              {team1Value.toFixed(1)}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-700">{team2}</span>
            <span className={`font-medium ${team2Wins ? 'text-green-600' : 'text-gray-900'}`}>
              {team2Value.toFixed(1)}
            </span>
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Running AI Prediction...</h2>
          <p className="text-gray-600">Analyzing team statistics and matchups</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            <strong className="font-bold">Error!</strong>
            <span className="block sm:inline"> {error}</span>
          </div>
          <button
            onClick={() => router.back()}
            className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  if (!prediction) return null;

  const winnerTeam = prediction.winner === team1.toUpperCase() ? team1Info : team2Info;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => router.back()}
            className="flex items-center text-blue-600 hover:text-blue-800 mb-4"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Games
          </button>
          <h1 className="text-3xl font-bold text-gray-900">Game Prediction</h1>
          <p className="text-gray-600 mt-2">
            {team1Info?.teamCity} {team1Info?.teamName} vs {team2Info?.teamCity} {team2Info?.teamName}
          </p>
        </div>

        {/* Prediction Result */}
        <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-8 mb-8">
          <div className="text-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">AI Prediction</h2>
            <div className="flex items-center justify-center space-x-4">
              {winnerTeam && (
                <div className="flex items-center space-x-3">
                  <img
                    src={winnerTeam.teamLogo}
                    alt={`${winnerTeam.teamName} logo`}
                    className="w-12 h-12 object-contain"
                  />
                  <span className="text-xl font-semibold text-gray-900">
                    {winnerTeam.teamCity} {winnerTeam.teamName}
                  </span>
                </div>
              )}
              <span className="text-lg text-gray-500">wins</span>
            </div>
            <div className="mt-4">
              <span className="inline-block bg-blue-100 text-blue-800 text-sm font-medium px-3 py-1 rounded-full">
                {prediction.confidence}% Confidence ({prediction.model_type})
              </span>
            </div>
          </div>

          {/* Win Probabilities */}
          {prediction.team1_win_probability && prediction.team2_win_probability && (
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-sm text-gray-600 mb-1">{team1} Win Probability</div>
                <div className="text-2xl font-bold text-blue-600">
                  {prediction.team1_win_probability}%
                </div>
              </div>
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-sm text-gray-600 mb-1">{team2} Win Probability</div>
                <div className="text-2xl font-bold text-blue-600">
                  {prediction.team2_win_probability}%
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Head to Head */}
        <div className="mb-8">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Head-to-Head Record</h3>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-blue-600">{prediction.head_to_head.team1_wins}</div>
                <div className="text-sm text-gray-600">{team1} Wins</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-400">{prediction.head_to_head.total}</div>
                <div className="text-sm text-gray-600">Total Games</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-red-600">{prediction.head_to_head.team2_wins}</div>
                <div className="text-sm text-gray-600">{team2} Wins</div>
              </div>
            </div>
          </div>
        </div>

        {/* Team Statistics Comparison */}
        <div className="mb-8">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Team Statistics Comparison</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <StatCard
              label="Win Percentage"
              team1Value={prediction.team1_stats.win_pct * 100}
              team2Value={prediction.team2_stats.win_pct * 100}
            />
            <StatCard
              label="Season Record"
              team1Value={prediction.team1_stats.wins}
              team2Value={prediction.team2_stats.wins}
            />
            <StatCard
              label="Recent Win %"
              team1Value={prediction.team1_stats.recent_win_pct * 100}
              team2Value={prediction.team2_stats.recent_win_pct * 100}
            />
            <StatCard
              label="Points Per Game"
              team1Value={prediction.team1_stats.avg_pts}
              team2Value={prediction.team2_stats.avg_pts}
            />
            <StatCard
              label="Points Allowed"
              team1Value={prediction.team1_stats.avg_pts_allowed}
              team2Value={prediction.team2_stats.avg_pts_allowed}
            />
            <StatCard
              label="Field Goal %"
              team1Value={prediction.team1_stats.fg_pct * 100}
              team2Value={prediction.team2_stats.fg_pct * 100}
            />
            <StatCard
              label="3-Point %"
              team1Value={prediction.team1_stats.fg3_pct * 100}
              team2Value={prediction.team2_stats.fg3_pct * 100}
            />
            <StatCard
              label="Free Throw %"
              team1Value={prediction.team1_stats.ft_pct * 100}
              team2Value={prediction.team2_stats.ft_pct * 100}
            />
            <StatCard
              label="Turnovers"
              team1Value={prediction.team1_stats.turnovers}
              team2Value={prediction.team2_stats.turnovers}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
