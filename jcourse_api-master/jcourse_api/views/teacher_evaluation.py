from django.db.models import Q
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from jcourse_api.models import TeacherEvaluation, Teacher
from jcourse_api.serializers.base import TeacherEvaluationSerializer, TeacherSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class TeacherEvaluationViewSet(viewsets.ReadOnlyModelViewSet):
    """教师评价视图集"""
    queryset = TeacherEvaluation.objects.all().select_related('teacher')
    serializer_class = TeacherEvaluationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['teacher', 'data_sources', 'evaluation_count']
    search_fields = ['teacher__name', 'evaluation_content']
    ordering_fields = ['created_at', 'evaluation_count']
    ordering = ['-created_at']

    @action(detail=False, methods=['get'])
    def search_by_teacher(self, request):
        """按教师姓名搜索评价"""
        teacher_name = request.query_params.get('name', '')
        if not teacher_name:
            return Response({'error': '请提供教师姓名'}, status=400)
        
        evaluations = self.queryset.filter(
            teacher__name__icontains=teacher_name
        )
        
        serializer = self.get_serializer(evaluations, many=True)
        return Response({
            'count': evaluations.count(),
            'results': serializer.data
        })

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取评价统计信息"""
        total_evaluations = TeacherEvaluation.objects.count()
        total_teachers = Teacher.objects.filter(evaluations__isnull=False).distinct().count()
        avg_evaluations_per_teacher = total_evaluations / total_teachers if total_teachers > 0 else 0
        
        # 按数据来源统计
        source_stats = {}
        for evaluation in TeacherEvaluation.objects.values('data_sources'):
            sources = evaluation['data_sources']
            if sources in source_stats:
                source_stats[sources] += 1
            else:
                source_stats[sources] = 1
        
        return Response({
            'total_evaluations': total_evaluations,
            'total_teachers_with_evaluations': total_teachers,
            'average_evaluations_per_teacher': round(avg_evaluations_per_teacher, 2),
            'source_statistics': source_stats
        })


class TeacherWithEvaluationViewSet(viewsets.ReadOnlyModelViewSet):
    """带评价的教师视图集"""
    queryset = Teacher.objects.prefetch_related('evaluations').all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'title']
    search_fields = ['name', 'pinyin', 'abbr_pinyin']
    ordering_fields = ['name']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def evaluations(self, request, pk=None):
        """获取特定教师的所有评价"""
        teacher = self.get_object()
        evaluations = teacher.evaluations.all()
        serializer = TeacherEvaluationSerializer(evaluations, many=True)
        return Response({
            'teacher': {
                'id': teacher.id,
                'name': teacher.name,
                'department': teacher.department.name if teacher.department else None,
                'title': teacher.title
            },
            'evaluation_count': evaluations.count(),
            'evaluations': serializer.data
        })

    @action(detail=False, methods=['get'])
    def with_evaluations(self, request):
        """获取有评价的教师列表"""
        teachers = self.queryset.filter(evaluations__isnull=False).distinct()
        
        # 分页
        page = self.paginate_queryset(teachers)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(teachers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search_evaluations(self, request):
        """搜索教师评价内容"""
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': '请提供搜索关键词'}, status=400)
        
        # 搜索教师姓名或评价内容
        teachers = self.queryset.filter(
            Q(name__icontains=query) | 
            Q(evaluations__evaluation_content__icontains=query)
        ).distinct()
        
        serializer = self.get_serializer(teachers, many=True)
        return Response({
            'query': query,
            'count': teachers.count(),
            'results': serializer.data
        })
