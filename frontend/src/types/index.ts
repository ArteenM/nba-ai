export interface Team {
  teamId: number;
  teamName: string;
  teamTricode: string;
  teamCity: string;
  teamSlug: string;
  wins: number;
  losses: number;
  score: number;
  seed: number;
  teamLogo: string;
  teamConference?: string;
  teamDivision?: string;
}

export interface Game {
  gameId: string;
  gameCode: string;
  gameStatus: number;
  gameStatusText: string;
  gameSequence: number;
  gameDateEst: string;
  gameTimeEst: string;
  gameDateTimeEst: string;
  gameDateUTC: string;
  gameTimeUTC: string;
  gameDateTimeUTC: string;
  awayTeamTime: string;
  homeTeamTime: string;
  day: string;
  monthNum: number;
  weekNumber: number;
  weekName: string;
  ifNecessary: boolean;
  seriesGameNumber: string;
  gameLabel: string;
  gameSubLabel: string;
  seriesText: string;
  arenaName: string;
  arenaState: string;
  arenaCity: string;
  postponedStatus: string;
  branchLink: string;
  gameSubtype: string;
  isNeutral: boolean;
  homeTeam: Team;
  awayTeam: Team;
  venue: {
    venueId: number;
    venueName: string;
    venueCity: string;
    venueState: string;
    venueCountry: string;
  };
  broadcasters: {
    nationalTvBroadcasters: Broadcaster[];
    nationalRadioBroadcasters: Broadcaster[];
    nationalOttBroadcasters: Broadcaster[];
    homeTvBroadcasters: Broadcaster[];
    homeRadioBroadcasters: Broadcaster[];
    homeOttBroadcasters: Broadcaster[];
    awayTvBroadcasters: Broadcaster[];
    awayRadioBroadcasters: Broadcaster[];
    awayOttBroadcasters: Broadcaster[];
    intlRadioBroadcasters: Broadcaster[];
    intlTvBroadcasters: Broadcaster[];
    intlOttBroadcasters: Broadcaster[];
  };
}

export interface Broadcaster {
  broadcasterScope: string;
  broadcasterMedia: string;
  broadcasterId: number;
  broadcasterDisplay: string;
  broadcasterAbbreviation: string;
  broadcasterDescription: string;
  tapeDelayComments: string;
  broadcasterVideoLink: string;
  regionId: number;
  broadcasterTeamId: number;
  broadcasterRanking: number | null;
  localizationRegion?: string;
}

export interface GameDate {
  gameDate: string;
  games: Game[];
}

export interface LeagueSchedule {
  seasonYear: string;
  leagueId: string;
  gameDates: GameDate[];
}

export interface ScheduleData {
  meta: {
    version: number;
    request: string;
    time: string;
  };
  leagueSchedule: LeagueSchedule;
}

export interface AppState {
  selectedDate: string; // YYYY-MM-DD format
  setSelectedDate: (date: string) => void;
}
