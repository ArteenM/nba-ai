from django.contrib import admin
from .models import Team, Season, Game, TeamStats, GamePrediction, PredictionModel

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'abbreviation', 'conference', 'division']
    list_filter = ['conference', 'division']
    search_fields = ['name', 'city', 'abbreviation']
    ordering = ['name']


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ['year', 'start_date', 'end_date', 'is_current']
    list_filter = ['is_current']
    ordering = ['-year']


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'status', 'home_score', 'away_score', 'game_date']
    list_filter = ['status', 'season', 'playoff_game', 'game_date']
    search_fields = ['home_team__name', 'away_team__name', 'nba_game_id']
    ordering = ['-game_date']
    date_hierarchy = 'game_date'


@admin.register(TeamStats)
class TeamStatsAdmin(admin.ModelAdmin):
    list_display = ['team', 'season', 'wins', 'losses', 'win_percentage', 'points_per_game']
    list_filter = ['season']
    search_fields = ['team__name']
    ordering = ['-season__year', '-win_percentage']


@admin.register(GamePrediction)
class GamePredictionAdmin(admin.ModelAdmin):
    list_display = ['game', 'predicted_winner', 'confidence_score', 'is_correct', 'created_at']
    list_filter = ['predicted_winner', 'is_correct', 'model_version']
    search_fields = ['game__home_team__name', 'game__away_team__name']
    ordering = ['-created_at']
    readonly_fields = ['is_correct']


@admin.register(PredictionModel)
class PredictionModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'version', 'algorithm', 'accuracy', 'is_active', 'created_at']
    list_filter = ['algorithm', 'is_active']
    search_fields = ['name', 'version']
    ordering = ['-created_at']