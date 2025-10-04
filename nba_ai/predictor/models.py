from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.

class Team(models.Model):
    """NBA Team model"""
    name = models.CharField(max_length=100, unique=True)
    abbreviation = models.CharField(max_length=5, unique=True)
    city = models.CharField(max_length=50)
    conference = models.CharField(max_length=10, choices=[('East', 'Eastern'), ('West', 'Western')])
    division = models.CharField(max_length=20)
    nba_team_id = models.IntegerField(unique=True)  # Official NBA API team ID
    founded_year = models.IntegerField(null=True, blank=True)

    # Team colors for UI
    primary_color = models.CharField(max_length=7, default='#000000')  # Hex color
    secondary_color = models.CharField(max_length=7, default='#FFFFFF')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.city} {self.name}"


class Season(models.Model):
    """NBA Season model"""
    year = models.CharField(max_length=9, unique=True)  # e.g., "2023-2024"
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-year']

    def __str__(self):
        return self.year


class Game(models.Model):
    """Individual NBA Game model"""
    GAME_STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('live', 'Live'),
        ('finished', 'Finished'),
        ('postponed', 'Postponed'),
        ('cancelled', 'Cancelled'),
    ]

    nba_game_id = models.CharField(max_length=20, unique=True)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_games')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_games')
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='games')

    game_date = models.DateTimeField()
    status = models.CharField(max_length=10, choices=GAME_STATUS_CHOICES, default='scheduled')

    # Game Results (null if game hasn't finished)
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    attendance = models.IntegerField(null=True, blank=True)

    # Game metadata
    playoff_game = models.BooleanField(default=False)
    game_type = models.CharField(max_length=20, default='Regular')  # Regular, Playoff, All-Star, etc.

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-game_date']
        unique_together = ['home_team', 'away_team', 'game_date']

    def __str__(self):
        return f"{self.away_team.abbreviation} @ {self.home_team.abbreviation} - {self.game_date.strftime('%Y-%m-%d')}"

    @property
    def winner(self):
        """Returns the winning team if game is finished"""
        if self.status == 'finished' and self.home_score and self.away_score:
            return self.home_team if self.home_score > self.away_score else self.away_team
        return None


class TeamStats(models.Model):
    """Team statistics for a specific season"""
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='season_stats')
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='team_stats')

    # Basic stats
    games_played = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    win_percentage = models.FloatField(default=0.0)

    # Offensive stats
    points_per_game = models.FloatField(default=0.0)
    field_goal_percentage = models.FloatField(default=0.0)
    three_point_percentage = models.FloatField(default=0.0)
    free_throw_percentage = models.FloatField(default=0.0)
    rebounds_per_game = models.FloatField(default=0.0)
    assists_per_game = models.FloatField(default=0.0)
    turnovers_per_game = models.FloatField(default=0.0)

    # Defensive stats
    opponent_points_per_game = models.FloatField(default=0.0)
    opponent_field_goal_percentage = models.FloatField(default=0.0)
    steals_per_game = models.FloatField(default=0.0)
    blocks_per_game = models.FloatField(default=0.0)

    # Advanced metrics
    offensive_rating = models.FloatField(default=0.0)  # Points per 100 possessions
    defensive_rating = models.FloatField(default=0.0)  # Opponent points per 100 possessions
    net_rating = models.FloatField(default=0.0)  # Off rating - Def rating
    pace = models.FloatField(default=0.0)  # Possessions per 48 minutes

    # Home/Away splits
    home_wins = models.IntegerField(default=0)
    home_losses = models.IntegerField(default=0)
    away_wins = models.IntegerField(default=0)
    away_losses = models.IntegerField(default=0)

    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['team', 'season']
        ordering = ['-season__year', '-win_percentage']

    def __str__(self):
        return f"{self.team.name} - {self.season.year}"


class GamePrediction(models.Model):
    """ML Predictions for NBA games"""
    game = models.OneToOneField(Game, on_delete=models.CASCADE, related_name='prediction')

    # Prediction results
    predicted_winner = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='predicted_wins')
    home_win_probability = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    away_win_probability = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )

    # Confidence metrics
    confidence_score = models.FloatField(default=0.0)  # Overall prediction confidence

    # Predicted scores (optional)
    predicted_home_score = models.FloatField(null=True, blank=True)
    predicted_away_score = models.FloatField(null=True, blank=True)
    predicted_total_points = models.FloatField(null=True, blank=True)

    # Model metadata
    model_version = models.CharField(max_length=50, default='v1.0')
    features_used = models.JSONField(default=list)  # List of features used in prediction

    # Tracking accuracy
    is_correct = models.BooleanField(null=True, blank=True)  # Set after game finishes

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Prediction: {self.game} - {self.predicted_winner.abbreviation} ({self.confidence_score:.2f})"

    def update_accuracy(self):
        """Update prediction accuracy after game finishes"""
        if self.game.status == 'finished' and self.game.winner:
            self.is_correct = (self.predicted_winner == self.game.winner)
            self.save()


class PredictionModel(models.Model):
    """Track different ML models and their performance"""
    name = models.CharField(max_length=100, unique=True)
    version = models.CharField(max_length=20)
    algorithm = models.CharField(max_length=50)  # e.g., "Random Forest", "XGBoost"

    # Model file path
    model_file_path = models.CharField(max_length=255)

    # Performance metrics
    accuracy = models.FloatField(default=0.0)
    precision = models.FloatField(default=0.0)
    recall = models.FloatField(default=0.0)
    f1_score = models.FloatField(default=0.0)

    # Training metadata
    training_data_start = models.DateField()
    training_data_end = models.DateField()
    features_used = models.JSONField(default=list)

    is_active = models.BooleanField(default=False)  # Currently used model

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['name', 'version']

    def __str__(self):
        return f"{self.name} v{self.version} ({self.algorithm})"
from django.db import models

# Create your models here.
