import { ScheduleData, Game, Team, GameDate } from '@/types';

let scheduleData: ScheduleData | null = null;

// Valid NBA team abbreviations (30 teams)
const validNBATeams = [
  'ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW',
  'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK',
  'OKC', 'ORL', 'PHI', 'PHX', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS'
];

// Helper function to check if a team is a valid NBA team
function isValidNBATeam(teamTricode: string): boolean {
  return validNBATeams.includes(teamTricode);
}

export async function loadScheduleData(): Promise<ScheduleData> {
  if (scheduleData) {
    return scheduleData;
  }

  try {
    const response = await fetch('/schedule.json');
    if (!response.ok) {
      throw new Error('Failed to load schedule data');
    }
    scheduleData = await response.json();
    return scheduleData!;
  } catch (error) {
    console.error('Error loading schedule data:', error);
    throw error;
  }
}

export async function getGamesForDate(date: string): Promise<Game[]> {
  const data = await loadScheduleData();
  const gameDate = data.leagueSchedule.gameDates.find(
    (gd: GameDate) => gd.gameDate === date
  );
  
  if (!gameDate) return [];
  
  // Filter and add logo URLs to teams in games (only NBA teams)
  return gameDate.games
    .filter(game => 
      isValidNBATeam(game.homeTeam.teamTricode) && 
      isValidNBATeam(game.awayTeam.teamTricode)
    )
    .map(game => ({
      ...game,
      homeTeam: {
        ...game.homeTeam,
        teamLogo: `/logos/${game.homeTeam.teamTricode}.png`
      },
      awayTeam: {
        ...game.awayTeam,
        teamLogo: `/logos/${game.awayTeam.teamTricode}.png`
      }
    }));
}

export async function getAllTeams(): Promise<Team[]> {
  const data = await loadScheduleData();
  const teamsMap = new Map<number, Team>();

  // Extract all unique NBA teams from all games
  data.leagueSchedule.gameDates.forEach((gameDate: GameDate) => {
    gameDate.games.forEach((game: Game) => {
      if (game.homeTeam && isValidNBATeam(game.homeTeam.teamTricode)) {
        const teamWithLogo = {
          ...game.homeTeam,
          teamLogo: `/logos/${game.homeTeam.teamTricode}.png`
        };
        teamsMap.set(game.homeTeam.teamId, teamWithLogo);
      }
      if (game.awayTeam && isValidNBATeam(game.awayTeam.teamTricode)) {
        const teamWithLogo = {
          ...game.awayTeam,
          teamLogo: `/logos/${game.awayTeam.teamTricode}.png`
        };
        teamsMap.set(game.awayTeam.teamId, teamWithLogo);
      }
    });
  });

  return Array.from(teamsMap.values());
}

export async function getTeamByAbbreviation(abbreviation: string): Promise<Team | null> {
  const teams = await getAllTeams();
  return teams.find(team => team.teamTricode === abbreviation) || null;
}

export async function getTeamSchedule(teamAbbreviation: string): Promise<Game[]> {
  const data = await loadScheduleData();
  const teamGames: Game[] = [];

  data.leagueSchedule.gameDates.forEach((gameDate: GameDate) => {
    gameDate.games.forEach((game: Game) => {
      if (game.homeTeam?.teamTricode === teamAbbreviation || game.awayTeam?.teamTricode === teamAbbreviation) {
        // Only include games with NBA teams
        if (isValidNBATeam(game.homeTeam.teamTricode) && isValidNBATeam(game.awayTeam.teamTricode)) {
          // Add logo URLs to teams in games
          const gameWithLogos = {
            ...game,
            homeTeam: {
              ...game.homeTeam,
              teamLogo: `/logos/${game.homeTeam.teamTricode}.png`
            },
            awayTeam: {
              ...game.awayTeam,
              teamLogo: `/logos/${game.awayTeam.teamTricode}.png`
            }
          };
          teamGames.push(gameWithLogos);
        }
      }
    });
  });

  return teamGames;
}

export async function getAvailableDates(): Promise<string[]> {
  const data = await loadScheduleData();
  return data.leagueSchedule.gameDates.map((gameDate: GameDate) => gameDate.gameDate);
}

// Helper function to format date for display
export function formatDateForDisplay(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
}

// Helper function to get today's date in the format used by the JSON
export function getTodayDateString(): string {
  const today = new Date();
  const month = String(today.getMonth() + 1).padStart(2, '0');
  const day = String(today.getDate()).padStart(2, '0');
  const year = today.getFullYear();
  return `${month}/${day}/${year} 00:00:00`;
}
