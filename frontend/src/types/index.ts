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

export interface TeamStats {
  abbreviation: string;
  win_pct: number;
  wins: number;
  losses: number;
  recent_win_pct: number;
  avg_pts: number;
  avg_pts_allowed: number;
  fg_pct: number;
  fg3_pct: number;
  ft_pct: number;
  off_reb: number;
  def_reb: number;
  turnovers: number;
  ast_to_to_ratio: number;
}

export interface HeadToHead {
  team1_wins: number;
  team2_wins: number;
  total: number;
  team1_win_pct: number;
  team2_win_pct: number;
}

export interface PredictionResult {
  winner: string;
  confidence: number;
  model_type: 'ML' | 'rule-based';
  team1_win_probability?: number;
  team2_win_probability?: number;
  team1_stats: TeamStats;
  team2_stats: TeamStats;
  head_to_head: HeadToHead;
}

export interface PredictionRequest {
  team1: string;
  team2: string;
}

export interface AppState {
  selectedDate: string; // YYYY-MM-DD format
  setSelectedDate: (date: string) => void;
}
