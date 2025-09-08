"""
Analytics API endpoints.

This module handles all analytics-related API endpoints including performance
metrics, usage statistics, and system monitoring data.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer

from app.models.analytics import (
    PerformanceMetrics,
    SystemMetrics,
    UsageStatistics,
    UserAnalytics,
)
from app.services.analytics_service import AnalyticsService
from app.utils.exceptions import ExternalServiceError

# Setup router and logging
router = APIRouter()
security = HTTPBearer()
logger = structlog.get_logger(__name__)


@router.get(
    "/metrics",
    response_model=PerformanceMetrics,
    summary="Get performance metrics",
    description="""
    Get comprehensive performance metrics including response times,
    token usage, error rates, and system performance data.
    """,
)
async def get_performance_metrics(
    start_date: Optional[datetime] = Query(None, description="Start date for metrics"),
    end_date: Optional[datetime] = Query(None, description="End date for metrics"),
    analytics_service: AnalyticsService = Depends(),
) -> PerformanceMetrics:
    """
    Get performance metrics for the specified time period.
    
    Args:
        start_date: Start date for metrics (optional, defaults to last 24 hours)
        end_date: End date for metrics (optional, defaults to now)
        analytics_service: Injected analytics service dependency
        
    Returns:
        PerformanceMetrics: Comprehensive performance metrics
        
    Raises:
        HTTPException: If metrics retrieval fails
    """
    try:
        # Set default time range if not provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(hours=24)
        
        logger.info(
            "Getting performance metrics",
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
        )
        
        metrics = await analytics_service.get_performance_metrics(
            start_date=start_date,
            end_date=end_date,
        )
        
        logger.info("Performance metrics retrieved successfully")
        return metrics
        
    except Exception as e:
        logger.error("Error getting performance metrics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve performance metrics",
        )


@router.get(
    "/usage",
    response_model=UsageStatistics,
    summary="Get usage statistics",
    description="""
    Get usage statistics including API calls, user activity,
    token consumption, and feature usage patterns.
    """,
)
async def get_usage_statistics(
    period: str = Query("day", regex="^(hour|day|week|month)$", description="Time period for statistics"),
    limit: int = Query(30, ge=1, le=365, description="Number of periods to return"),
    analytics_service: AnalyticsService = Depends(),
) -> UsageStatistics:
    """
    Get usage statistics for the specified period.
    
    Args:
        period: Time period for aggregation (hour, day, week, month)
        limit: Number of periods to return
        analytics_service: Injected analytics service dependency
        
    Returns:
        UsageStatistics: Usage statistics and trends
        
    Raises:
        HTTPException: If statistics retrieval fails
    """
    try:
        logger.info("Getting usage statistics", period=period, limit=limit)
        
        statistics = await analytics_service.get_usage_statistics(
            period=period,
            limit=limit,
        )
        
        logger.info("Usage statistics retrieved successfully")
        return statistics
        
    except Exception as e:
        logger.error("Error getting usage statistics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve usage statistics",
        )


@router.get(
    "/system",
    response_model=SystemMetrics,
    summary="Get system metrics",
    description="""
    Get system health and performance metrics including memory usage,
    CPU utilization, database performance, and external service status.
    """,
)
async def get_system_metrics(
    analytics_service: AnalyticsService = Depends(),
) -> SystemMetrics:
    """
    Get current system metrics and health status.
    
    Args:
        analytics_service: Injected analytics service dependency
        
    Returns:
        SystemMetrics: System health and performance metrics
        
    Raises:
        HTTPException: If metrics retrieval fails
    """
    try:
        logger.info("Getting system metrics")
        
        metrics = await analytics_service.get_system_metrics()
        
        logger.info("System metrics retrieved successfully")
        return metrics
        
    except Exception as e:
        logger.error("Error getting system metrics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system metrics",
        )


@router.get(
    "/users/{user_id}",
    response_model=UserAnalytics,
    summary="Get user analytics",
    description="""
    Get analytics data for a specific user including usage patterns,
    conversation metrics, and performance statistics.
    """,
)
async def get_user_analytics(
    user_id: str,
    start_date: Optional[datetime] = Query(None, description="Start date for analytics"),
    end_date: Optional[datetime] = Query(None, description="End date for analytics"),
    analytics_service: AnalyticsService = Depends(),
) -> UserAnalytics:
    """
    Get analytics data for a specific user.
    
    Args:
        user_id: User identifier
        start_date: Start date for analytics (optional)
        end_date: End date for analytics (optional)
        analytics_service: Injected analytics service dependency
        
    Returns:
        UserAnalytics: User-specific analytics data
        
    Raises:
        HTTPException: If user not found or analytics retrieval fails
    """
    try:
        # Set default time range if not provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        logger.info(
            "Getting user analytics",
            user_id=user_id,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
        )
        
        analytics = await analytics_service.get_user_analytics(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
        )
        
        if not analytics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found or has no analytics data",
            )
        
        logger.info("User analytics retrieved successfully", user_id=user_id)
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting user analytics", error=str(e), user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user analytics",
        )


@router.get(
    "/trends",
    response_model=Dict[str, List[Dict]],
    summary="Get analytics trends",
    description="""
    Get trending data across various metrics including popular features,
    common queries, performance trends, and usage patterns.
    """,
)
async def get_analytics_trends(
    metric: str = Query("all", description="Specific metric to analyze"),
    period: str = Query("day", regex="^(hour|day|week|month)$", description="Time period for trends"),
    limit: int = Query(10, ge=1, le=100, description="Number of trend items to return"),
    analytics_service: AnalyticsService = Depends(),
) -> Dict[str, List[Dict]]:
    """
    Get trending analytics data.
    
    Args:
        metric: Specific metric to analyze (all, queries, features, errors)
        period: Time period for trend analysis
        limit: Number of trend items to return
        analytics_service: Injected analytics service dependency
        
    Returns:
        Dict[str, List[Dict]]: Trending data across various metrics
        
    Raises:
        HTTPException: If trends retrieval fails
    """
    try:
        logger.info("Getting analytics trends", metric=metric, period=period, limit=limit)
        
        trends = await analytics_service.get_analytics_trends(
            metric=metric,
            period=period,
            limit=limit,
        )
        
        logger.info("Analytics trends retrieved successfully")
        return trends
        
    except Exception as e:
        logger.error("Error getting analytics trends", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics trends",
        )


@router.post(
    "/track",
    summary="Track custom event",
    description="""
    Track a custom analytics event for monitoring and analysis.
    This endpoint allows logging custom events for business intelligence.
    """,
)
async def track_event(
    event_data: Dict[str, any],
    analytics_service: AnalyticsService = Depends(),
) -> dict:
    """
    Track a custom analytics event.
    
    Args:
        event_data: Event data to track
        analytics_service: Injected analytics service dependency
        
    Returns:
        dict: Confirmation of event tracking
        
    Raises:
        HTTPException: If event tracking fails
    """
    try:
        logger.info("Tracking custom event", event_type=event_data.get("type", "unknown"))
        
        await analytics_service.track_event(event_data)
        
        logger.info("Custom event tracked successfully")
        
        return {
            "message": "Event tracked successfully",
            "timestamp": datetime.utcnow().isoformat(),
        }
        
    except Exception as e:
        logger.error("Error tracking event", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to track event",
        )
