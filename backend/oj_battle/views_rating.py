"""
对战排行榜相关视图
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q

from .models import BattleRating, BattleSeason, BattleResult
from .serializers import BattleRatingSerializer, BattleSeasonSerializer, BattleResultSerializer


@api_view(['GET'])
def leaderboard(request):
    """
    获取排行榜
    支持按赛季筛选
    """
    season_id = request.query_params.get('season_id')
    
    # 获取当前赛季
    current_season = BattleSeason.get_current_season()
    
    # 如果没有指定赛季，使用当前赛季
    if not season_id and current_season:
        season_id = current_season.id
    
    # 查询排行榜数据
    if season_id:
        ratings = BattleRating.objects.filter(
            season_id=season_id
        ).select_related('user').order_by('-rating', '-peak_rating')[:100]
    else:
        # 如果没有赛季，显示所有用户的最新数据
        ratings = BattleRating.objects.filter(
            season__isnull=True
        ).select_related('user').order_by('-rating', '-peak_rating')[:100]
    
    serializer = BattleRatingSerializer(ratings, many=True)
    
    return Response({
        'current_season': BattleSeasonSerializer(current_season).data if current_season else None,
        'leaderboard': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_rating(request):
    """
    获取当前用户的等级分信息
    """
    season_id = request.query_params.get('season_id')
    
    # 获取当前赛季
    current_season = BattleSeason.get_current_season()
    
    # 如果没有指定赛季，使用当前赛季
    if not season_id and current_season:
        season_id = current_season.id
    
    try:
        if season_id:
            rating = BattleRating.objects.get(user=request.user, season_id=season_id)
        else:
            rating = BattleRating.objects.get(user=request.user, season__isnull=True)
    except BattleRating.DoesNotExist:
        # 如果不存在，返回默认值
        return Response({
            'rating': None,
            'current_season': BattleSeasonSerializer(current_season).data if current_season else None
        })
    
    serializer = BattleRatingSerializer(rating)
    
    return Response({
        'rating': serializer.data,
        'current_season': BattleSeasonSerializer(current_season).data if current_season else None
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def battle_history(request):
    """
    获取对战历史
    """
    user_id = request.query_params.get('user_id', request.user.id)
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    
    # 查询用户参与的对战
    results = BattleResult.objects.filter(
        Q(user_a_id=user_id) | Q(user_b_id=user_id)
    ).select_related('user_a', 'user_b', 'winner', 'season').order_by('-created_at')
    
    # 分页
    start = (page - 1) * page_size
    end = start + page_size
    total = results.count()
    results = results[start:end]
    
    serializer = BattleResultSerializer(results, many=True)
    
    return Response({
        'total': total,
        'page': page,
        'page_size': page_size,
        'results': serializer.data
    })


@api_view(['GET'])
def seasons(request):
    """
    获取所有赛季列表
    """
    seasons = BattleSeason.objects.all().order_by('-start_time')
    serializer = BattleSeasonSerializer(seasons, many=True)
    
    return Response({
        'seasons': serializer.data
    })
