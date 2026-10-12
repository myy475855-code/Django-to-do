from django.contrib.auth.models import User
from django.db.models import F
from django.utils import timezone
from rest_framework import generics, permissions, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Task
from .permissions import IsOwner
from .serializers import TaskSerializer, RegisterSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description', 'category']

    def get_queryset(self):
        qs = Task.objects.filter(owner=self.request.user)
        p = self.request.query_params
        if p.get('completed') is not None:
            qs = qs.filter(completed=p['completed'].lower() == 'true')
        if p.get('priority') in ('1', '2', '3'):
            qs = qs.filter(priority=int(p['priority']))
        if p.get('sort') == 'due':
            qs = qs.order_by(F('due_date').asc(nulls_last=True), '-priority')
        elif p.get('sort') == 'priority':
            qs = qs.order_by('-priority', '-created_at')
        return qs

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = Task.objects.filter(owner=request.user)
        return Response({
            'total': qs.count(),
            'done': qs.filter(completed=True).count(),
            'overdue': qs.filter(completed=False, due_date__lt=timezone.localdate()).count(),
        })

    @action(detail=False, methods=['post'])
    def clear_completed(self, request):
        n, _ = Task.objects.filter(owner=request.user, completed=True).delete()
        return Response({'deleted': n})
