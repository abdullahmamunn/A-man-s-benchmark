from datetime import timedelta
from django.db.models import Sum, Max, Q, Case, When, Value, IntegerField
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import (
    Task, ScoreArea, WeeklyScore, StudySession, WeeklyReview, UserSettings,
    TaskCategory, TaskPriority, TaskStatus
)
from .serializers import (
    TaskSerializer, ScoreAreaSerializer, WeeklyScoreSerializer,
    StudySessionSerializer, WeeklyReviewSerializer, UserSettingsSerializer
)
from .time import local_today

def get_request_user(request):
    return request.user

class TaskViewSet(viewsets.ModelViewSet):
    """
    CRUD API for Tasks.
    Automatically applies Academy First sorting: University Coursework strictly first!
    """
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = get_request_user(self.request)
        qs = Task.objects.filter(user=user)

        # Multi-criteria filtering
        category = self.request.query_params.get('category')
        priority = self.request.query_params.get('priority')
        task_status = self.request.query_params.get('status')
        sort_by = self.request.query_params.get('sort', 'academy_first')

        if category and category != 'All':
            qs = qs.filter(category=category)
        if priority and priority != 'All':
            qs = qs.filter(priority=priority)
        if task_status and task_status != 'All':
            qs = qs.filter(status=task_status)

        # Academy First custom sorting:
        # 1. Coursework = 0, Other = 1
        # 2. Priority: High = 3, Medium = 2, Low = 1
        # 3. Due Date
        if sort_by == 'due_date':
            return qs.order_by('due_date', '-priority')
        elif sort_by == 'priority':
            return qs.annotate(
                p_rank=Case(
                    When(priority='High', then=Value(3)),
                    When(priority='Medium', then=Value(2)),
                    default=Value(1),
                    output_field=IntegerField()
                )
            ).order_by('-p_rank', 'due_date')
        elif sort_by == 'status':
            return qs.order_by('status', 'due_date')
        else:
            # Default: Academy First
            return qs.annotate(
                academy_rank=Case(
                    When(category=TaskCategory.UNIVERSITY_COURSEWORK, then=Value(0)),
                    default=Value(1),
                    output_field=IntegerField()
                ),
                priority_rank=Case(
                    When(priority='High', then=Value(3)),
                    When(priority='Medium', then=Value(2)),
                    default=Value(1),
                    output_field=IntegerField()
                ),
                completed_rank=Case(
                    When(status=TaskStatus.COMPLETED, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField()
                )
            ).order_by('completed_rank', 'academy_rank', '-priority_rank', 'due_date')

    def perform_create(self, serializer):
        serializer.save(user=get_request_user(self.request))

    @action(detail=True, methods=['post', 'patch'])
    def toggle_complete(self, request, pk=None):
        task = self.get_object()
        task.status = TaskStatus.PENDING if task.status == TaskStatus.COMPLETED else TaskStatus.COMPLETED
        task.save()
        return Response(TaskSerializer(task).data)

class ScoreAreaViewSet(viewsets.ReadOnlyModelViewSet):
    """Returns the 5 core evaluation pillars."""
    queryset = ScoreArea.objects.all().order_by('order')
    serializer_class = ScoreAreaSerializer

class WeeklyScoreViewSet(viewsets.ModelViewSet):
    """
    Evidence-based weekly ratings.
    Enforces uniqueness per (user, score_area, week_start).
    """
    serializer_class = WeeklyScoreSerializer

    def get_queryset(self):
        user = get_request_user(self.request)
        qs = WeeklyScore.objects.filter(user=user)
        week_start = self.request.query_params.get('week_start')
        if week_start:
            qs = qs.filter(week_start=week_start)
        return qs.order_by('-week_start', 'score_area__order')

    def create(self, request, *args, **kwargs):
        user = get_request_user(request)
        score_area_id = request.data.get('score_area')
        week_start = request.data.get('week_start')

        # Upsert: if already exists for this week, update rating & evidence
        existing = WeeklyScore.objects.filter(user=user, score_area_id=score_area_id, week_start=week_start).first()
        if existing:
            serializer = self.get_serializer(existing, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class StudySessionViewSet(viewsets.ModelViewSet):
    """Logs deep work sessions and calculates study volumes."""
    serializer_class = StudySessionSerializer

    def get_queryset(self):
        user = get_request_user(self.request)
        return StudySession.objects.filter(user=user).order_by('-date', '-created_at')

    def perform_create(self, serializer):
        serializer.save(user=get_request_user(self.request))

class WeeklyReviewViewSet(viewsets.ModelViewSet):
    """Weekly strategic reflection and debrief."""
    serializer_class = WeeklyReviewSerializer

    def get_queryset(self):
        user = get_request_user(self.request)
        return WeeklyReview.objects.filter(user=user).order_by('-week_start')

    def create(self, request, *args, **kwargs):
        user = get_request_user(request)
        week_start = request.data.get('week_start')

        existing = WeeklyReview.objects.filter(user=user, week_start=week_start).first()
        if existing:
            serializer = self.get_serializer(existing, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UserSettingsView(APIView):
    """Retrieve and update user targets and PR records to beat."""
    def get(self, request):
        user = get_request_user(request)
        settings_obj, _ = UserSettings.objects.get_or_create(user=user)
        serializer = UserSettingsSerializer(settings_obj)
        return Response(serializer.data)

    def post(self, request):
        user = get_request_user(request)
        settings_obj, _ = UserSettings.objects.get_or_create(user=user)
        serializer = UserSettingsSerializer(settings_obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class DashboardSummaryView(APIView):
    """
    Consolidated Dashboard summary endpoint:
    - Academy Standing Card metrics (Execution vs 90% target)
    - PR Challenge metrics (Current week vs all-time PR, single session PR)
    - 4 Summary KPI cards
    - Today's & Urgent Priorities (Academy First)
    - Scoreboard Preview (5 Pillars)
    - 7-Day Study Activity
    """
    def get(self, request):
        user = get_request_user(request)
        settings_obj, _ = UserSettings.objects.get_or_create(user=user)

        # 1. Academy Tasks
        tasks = Task.objects.filter(user=user)
        academy_tasks = tasks.filter(category=TaskCategory.UNIVERSITY_COURSEWORK)
        academy_total = academy_tasks.count()
        academy_completed = academy_tasks.filter(status=TaskStatus.COMPLETED).count()
        academy_rate = round((academy_completed / academy_total) * 100) if academy_total > 0 else 0

        # Update settings current execution
        settings_obj.current_execution_rate = academy_rate
        settings_obj.save(update_fields=['current_execution_rate'])

        # 2. Study Session calculations (Current 7 days vs Prior 7 days)
        today = local_today(settings_obj)
        seven_days_ago = today - timedelta(days=7)
        fourteen_days_ago = today - timedelta(days=14)

        current_week_mins = StudySession.objects.filter(
            user=user, date__gte=seven_days_ago, date__lte=today
        ).aggregate(total=Sum('duration_minutes'))['total'] or 0

        prior_week_mins = StudySession.objects.filter(
            user=user, date__gte=fourteen_days_ago, date__lt=seven_days_ago
        ).aggregate(total=Sum('duration_minutes'))['total'] or 0

        current_week_hours = round(current_week_mins / 60.0, 1)
        prior_week_hours = round(prior_week_mins / 60.0, 1)
        study_delta = round(current_week_hours - prior_week_hours, 1)
        delta_percent = round(((current_week_hours - prior_week_hours) / prior_week_hours) * 100) if prior_week_hours > 0 else 0

        longest_session_mins = StudySession.objects.filter(
            user=user, date__gte=seven_days_ago, date__lte=today
        ).aggregate(longest=Max('duration_minutes'))['longest'] or 0

        # 3. Scoreboard preview
        pillars = ScoreArea.objects.all().order_by('order')
        scoreboard_preview = []
        recent_ratings = []
        for p in pillars:
            latest_score = WeeklyScore.objects.filter(user=user, score_area=p).order_by('-week_start').first()
            if latest_score:
                recent_ratings.append(latest_score.rating)
            scoreboard_preview.append({
                'id': p.id,
                'title': p.title,
                'code': p.code,
                'priority_tag': p.priority_tag,
                'rating': latest_score.rating if latest_score else 0,
                'evidence': latest_score.evidence if latest_score else "No evaluation logged."
            })

        scoreboard_avg = round(sum(recent_ratings) / len(recent_ratings), 1) if recent_ratings else 0

        # 4. Limit-Breaker Index: 40% Academy, 35% Study PR, 25% Pillar Avg
        pr_target = settings_obj.weekly_study_pr_hours or 0
        pr_ratio = min(1.0, current_week_hours / pr_target) if pr_target > 0 else 0
        academy_ratio = academy_rate / 100.0
        scoreboard_ratio = min(1.0, scoreboard_avg / 5.0)

        limit_breaker_index = min(100, round(
            (academy_ratio * 40.0) + (pr_ratio * 35.0) + (scoreboard_ratio * 25.0)
        ))

        # 5. Urgent Tasks (Academy First)
        urgent_tasks = tasks.filter(~Q(status=TaskStatus.COMPLETED)).annotate(
            academy_rank=Case(
                When(category=TaskCategory.UNIVERSITY_COURSEWORK, then=Value(0)),
                default=Value(1),
                output_field=IntegerField()
            ),
            priority_rank=Case(
                When(priority='High', then=Value(3)),
                When(priority='Medium', then=Value(2)),
                default=Value(1),
                output_field=IntegerField()
            )
        ).order_by('academy_rank', '-priority_rank', 'due_date')[:5]

        # 6. 7-day study activity chart
        daily_activity = []
        for i in range(6, -1, -1):
            day_date = today - timedelta(days=i)
            day_mins = StudySession.objects.filter(user=user, date=day_date).aggregate(total=Sum('duration_minutes'))['total'] or 0
            daily_activity.append({
                'date': day_date.strftime('%Y-%m-%d'),
                'label': day_date.strftime('%a'),
                'hours': round(day_mins / 60.0, 1)
            })

        pending_count = tasks.filter(~Q(status=TaskStatus.COMPLETED)).count()
        high_priority_pending = tasks.filter(~Q(status=TaskStatus.COMPLETED), priority='High').count()

        return Response({
            'today': today.isoformat(),
            'settings': UserSettingsSerializer(settings_obj).data,
            'academy_standing': {
                'current_execution': academy_rate,
                'target_execution': settings_obj.target_execution_rate,
                'completed_count': academy_completed,
                'total_count': academy_total,
                'completion_rate': academy_rate,
                'target_delta': round(academy_rate - settings_obj.target_execution_rate, 1)
            },
            'pr_challenge': {
                'weekly_intention': settings_obj.weekly_intention,
                'current_week_hours': current_week_hours,
                'weekly_pr_hours': settings_obj.weekly_study_pr_hours,
                'pr_progress_percent': min(100, round((current_week_hours / settings_obj.weekly_study_pr_hours) * 100)) if settings_obj.weekly_study_pr_hours else 0,
                'longest_session_this_week_mins': longest_session_mins,
                'single_session_pr_mins': settings_obj.longest_session_pr_minutes,
                'longest_session_progress_percent': min(100, round((longest_session_mins / settings_obj.longest_session_pr_minutes) * 100)) if settings_obj.longest_session_pr_minutes else 0
            },
            'kpis': {
                'academy_completed': academy_completed,
                'academy_total': academy_total,
                'academy_completion_rate': academy_rate,
                'pending_count': pending_count,
                'high_priority_pending_count': high_priority_pending,
                'study_hours_current': current_week_hours,
                'study_hours_prior': prior_week_hours,
                'study_hours_delta': study_delta,
                'study_hours_delta_percent': delta_percent,
                'study_record_to_beat': settings_obj.weekly_study_pr_hours,
                'limit_breaker_index': limit_breaker_index
            },
            'urgent_tasks': TaskSerializer(urgent_tasks, many=True).data,
            'scoreboard_preview': scoreboard_preview,
            'weekly_study_chart': daily_activity
        })
