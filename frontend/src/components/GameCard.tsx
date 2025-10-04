import { Game } from '@/types';

interface GameCardProps {
  game: Game;
}

export default function GameCard({ game }: GameCardProps) {
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
    <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6 hover:shadow-lg transition-shadow duration-200">
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
        <div className="text-center text-xs text-gray-500">
          {game.arenaName}
          {game.arenaCity && ` • ${game.arenaCity}`}
        </div>
      </div>
    </div>
  );
}
