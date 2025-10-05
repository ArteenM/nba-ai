import { Game } from '@/types';
import { useRouter } from 'next/navigation';

interface GameCardProps {
  game: Game;
}

export default function GameCard({ game }: GameCardProps) {
  const router = useRouter();

  const handleGameClick = () => {
    // Navigate to prediction page
    router.push(`/prediction/${game.homeTeam.teamTricode}/${game.awayTeam.teamTricode}`);
  };
  const formatGameTime = (dateTimeUTC: string) => {
    const date = new Date(dateTimeUTC);
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  };

  const getGameStatusColor = (status: number) => {
    switch (status) {
      case 1: return 'text-yellow-600'; // Scheduled
      case 2: return 'text-green-600';  // Live
      case 3: return 'text-gray-600';   // Final
      default: return 'text-gray-500';
    }
  };

  const getGameStatusText = (status: number, statusText: string) => {
    if (status === 2) return 'LIVE';
    return statusText;
  };

  return (
    <div 
      className="bg-white rounded-lg shadow-md border border-gray-200 p-6 hover:shadow-lg transition-shadow duration-200 cursor-pointer"
      onClick={handleGameClick}
    >
      {/* Game Status */}
      <div className="text-center mb-4">
        <span className={`text-sm font-medium ${getGameStatusColor(game.gameStatus)}`}>
          {getGameStatusText(game.gameStatus, game.gameStatusText)}
        </span>
        {game.gameStatus === 1 && (
          <div className="text-xs text-gray-500 mt-1">
            {formatGameTime(game.gameDateTimeUTC)}
          </div>
        )}
      </div>

      {/* Teams */}
      <div className="flex items-center justify-between">
        {/* Away Team */}
        <div className="flex flex-col items-center flex-1">
          <div className="w-16 h-16 mb-2 flex items-center justify-center">
            <img
              src={game.awayTeam.teamLogo}
              alt={`${game.awayTeam.teamName} logo`}
              className="w-full h-full object-contain"
              onError={(e) => {
                // Fallback to team abbreviation if logo fails to load
                const target = e.target as HTMLImageElement;
                target.style.display = 'none';
                const parent = target.parentElement;
                if (parent) {
                  parent.innerHTML = `<div class="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center text-sm font-bold text-gray-600">${game.awayTeam.teamTricode}</div>`;
                }
              }}
            />
          </div>
          <div className="text-center">
            <div className="font-medium text-gray-900 text-sm">
              {game.awayTeam.teamCity}
            </div>
            <div className="text-xs text-gray-600">
              {game.awayTeam.teamName}
            </div>
          </div>
        </div>

        {/* VS */}
        <div className="flex flex-col items-center mx-4">
          <div className="text-gray-400 text-sm font-medium">at</div>
          {game.isNeutral && (
            <div className="text-xs text-gray-500 mt-1 text-center">
              {game.arenaCity}
            </div>
          )}
        </div>

        {/* Home Team */}
        <div className="flex flex-col items-center flex-1">
          <div className="w-16 h-16 mb-2 flex items-center justify-center">
            <img
              src={game.homeTeam.teamLogo}
              alt={`${game.homeTeam.teamName} logo`}
              className="w-full h-full object-contain"
              onError={(e) => {
                // Fallback to team abbreviation if logo fails to load
                const target = e.target as HTMLImageElement;
                target.style.display = 'none';
                const parent = target.parentElement;
                if (parent) {
                  parent.innerHTML = `<div class="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center text-sm font-bold text-gray-600">${game.homeTeam.teamTricode}</div>`;
                }
              }}
            />
          </div>
          <div className="text-center">
            <div className="font-medium text-gray-900 text-sm">
              {game.homeTeam.teamCity}
            </div>
            <div className="text-xs text-gray-600">
              {game.homeTeam.teamName}
            </div>
          </div>
        </div>
      </div>

      {/* Arena Info */}
      <div className="mt-4 pt-4 border-t border-gray-100">
        <div className="text-center text-xs text-gray-500 mb-3">
          {game.arenaName}
          {game.arenaCity && ` • ${game.arenaCity}`}
        </div>
        <div className="text-center">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            Predict Winner
          </span>
        </div>
      </div>
    </div>
  );
}
