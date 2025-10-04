# HoopPredict - NBA Game Predictor Frontend

A modern, desktop-only Next.js application for NBA game predictions and team analysis. Built with TypeScript, TailwindCSS, and Zustand for state management.

## Features

### 🏀 Dashboard
- View today's NBA games in a clean 3-column grid layout
- Date navigation with previous/next buttons and "Today" shortcut
- Timezone selector for global users
- Real-time game status indicators (Scheduled, Live, Final)
- Game cards with team logos, names, and arena information

### 👥 Teams
- Browse all NBA teams with logos and records
- Click any team to view detailed information
- Team-specific game schedules and statistics

### 📊 Team Details
- Full team information with logo and record
- Upcoming games with opponent details
- Simulated AI analysis with full-page loading overlay
- Home/Away game indicators

### ℹ️ About
- Detailed explanation of the AI model's functionality
- Information about the development team and mission

## Tech Stack

- **Next.js 14** (App Router)
- **TypeScript** for type safety
- **TailwindCSS** for styling
- **Zustand** for global state management
- **Luxon** for timezone handling (ready for implementation)

## Project Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── page.tsx           # Dashboard (home page)
│   ├── teams/             # Teams pages
│   │   ├── page.tsx       # Teams listing
│   │   └── [abbr]/        # Dynamic team details
│   │       └── page.tsx
│   ├── about/             # About page
│   │   └── page.tsx
│   └── layout.tsx         # Root layout
├── components/            # Reusable components
│   ├── Header.tsx         # Global header with navigation
│   └── GameCard.tsx       # Game card component
├── lib/                   # Utility functions
│   └── dataSource.ts      # Data access layer
├── store/                 # State management
│   └── appStore.ts        # Zustand store
└── types/                 # TypeScript definitions
    └── index.ts           # Type interfaces
```

## Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

### Building for Production

```bash
npm run build
npm start
```

## Data Source

The application currently reads from a local `schedule.json` file located in the `public` directory. This file contains:

- Complete NBA schedule data
- Team information (names, abbreviations, cities)
- Game details (times, venues, status)
- Team records and statistics

### Data Structure

The JSON follows the NBA API format with:
- `leagueSchedule.gameDates[]` - Array of game dates
- `games[]` - Array of games for each date
- `homeTeam`/`awayTeam` - Team objects with IDs, names, cities, etc.

## State Management

Global state is managed using Zustand with the following keys:
- `selectedDate` - Currently selected date (YYYY-MM-DD format)
- `timezone` - Selected timezone (IANA string)

## Backend Integration Ready

The application is structured for easy backend integration:

### Data Access Layer
All data access goes through `src/lib/dataSource.ts`, making it simple to replace with API calls:

```typescript
// Current: Local JSON file
const data = await loadScheduleData();

// Future: API calls
const data = await fetch('/api/schedule');
```

### Planned API Endpoints
- `GET /api/games?date=YYYY-MM-DD` - Get games for specific date
- `GET /api/teams` - Get all teams
- `GET /api/teams/:abbr/schedule` - Get team schedule

## UI/UX Features

### Desktop-Only Design
- Optimized for desktop viewing with max-width containers
- 3-column grid layout for game cards
- Responsive design that works on tablets and larger screens

### Loading States
- Skeleton loading animations for initial data load
- Full-page AI analysis overlay for team details
- Smooth transitions and hover effects

### Error Handling
- Graceful error states with user-friendly messages
- Fallback UI for missing team logos
- Network error handling

## Customization

### Styling
The application uses TailwindCSS with a clean, minimal design. Key design tokens:
- Primary colors: Blue (#3B82F6) and Gray (#6B7280)
- Card shadows and rounded corners for depth
- Consistent spacing and typography

### Adding New Features
1. Create new pages in `src/app/`
2. Add components in `src/components/`
3. Update types in `src/types/index.ts`
4. Extend the data source in `src/lib/dataSource.ts`

## Development

### Code Quality
- TypeScript for type safety
- ESLint for code linting
- Prettier for code formatting
- Consistent file naming and structure

### Performance
- Client-side data caching
- Optimized image loading with fallbacks
- Efficient re-renders with React hooks

## Future Enhancements

- [ ] Real-time game updates
- [ ] User authentication and preferences
- [ ] Advanced filtering and search
- [ ] Mobile-responsive design
- [ ] Dark mode theme
- [ ] Push notifications for live games
- [ ] Social sharing features

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the NBA-AI hackathon project. See the main repository for licensing information.