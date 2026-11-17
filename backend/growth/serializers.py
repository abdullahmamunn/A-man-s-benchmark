from rest_framework import serializers
from .models import Task, ScoreArea, WeeklyScore, StudySession, WeeklyReview, UserSettings

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'category', 'priority',
            'due_date', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Task title cannot be empty.")
        return value.strip()

class ScoreAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoreArea
        fields = ['id', 'code', 'title', 'priority_tag', 'description', 'order']

class WeeklyScoreSerializer(serializers.ModelSerializer):
    score_area_title = serializers.ReadOnlyField(source='score_area.title')
    score_area_code = serializers.ReadOnlyField(source='score_area.code')

    class Meta:
        model = WeeklyScore
        fields = [
            'id', 'score_area', 'score_area_title', 'score_area_code',
            'week_start', 'rating', 'evidence', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_evidence(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Mandatory objective evidence is required. Cite concrete metrics.")
        return value.strip()

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be an integer between 1 and 5.")
        return value

class StudySessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudySession
        fields = ['id', 'subject', 'date', 'duration_minutes', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_duration_minutes(self, value):
        if value <= 0:
            raise serializers.ValidationError("Duration must be greater than zero minutes.")
        return value

class WeeklyReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyReview
        fields = [
            'id', 'week_start', 'accomplishments', 'failures', 'distractions',
            'lessons_learned', 'next_week_improvements',
            'non_negotiable_1', 'non_negotiable_2', 'non_negotiable_3',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_non_negotiable_1(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Non-Negotiable Priority #1 (Academy Standing) is required.")
        return value.strip()

class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = [
            'student_name', 'aspiration', 'major', 'gpa_target',
            'current_execution_rate', 'target_execution_rate',
            'weekly_study_pr_hours', 'longest_session_pr_minutes',
            'weekly_intention'
        ]
