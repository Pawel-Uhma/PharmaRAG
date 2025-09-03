"""
Performance monitoring module for PharmaRAG service.
Tracks database operations and provides optimization insights.
"""

import time
import threading
import logging
from typing import Dict, Any, Optional
from collections import defaultdict, deque
from datetime import datetime, timedelta

try:
    from .config import ENABLE_PERFORMANCE_MONITORING, PERFORMANCE_LOG_THRESHOLD_MS
except ImportError:
    from config import ENABLE_PERFORMANCE_MONITORING, PERFORMANCE_LOG_THRESHOLD_MS

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitors and tracks performance metrics for database operations."""
    
    def __init__(self):
        self.metrics = defaultdict(lambda: {
            'count': 0,
            'total_time': 0.0,
            'min_time': float('inf'),
            'max_time': 0.0,
            'recent_times': deque(maxlen=100)  # Keep last 100 measurements
        })
        self.lock = threading.Lock()
        self.start_time = time.time()
    
    def record_operation(self, operation_name: str, duration_ms: float):
        """Record performance metrics for an operation."""
        if not ENABLE_PERFORMANCE_MONITORING:
            return
        
        with self.lock:
            metric = self.metrics[operation_name]
            metric['count'] += 1
            metric['total_time'] += duration_ms
            metric['min_time'] = min(metric['min_time'], duration_ms)
            metric['max_time'] = max(metric['max_time'], duration_ms)
            metric['recent_times'].append(duration_ms)
            
            # Log slow operations
            if duration_ms > PERFORMANCE_LOG_THRESHOLD_MS:
                logger.warning(f"Slow operation detected: {operation_name} took {duration_ms:.2f}ms")
    
    def get_operation_stats(self, operation_name: str) -> Dict[str, Any]:
        """Get statistics for a specific operation."""
        with self.lock:
            if operation_name not in self.metrics:
                return {}
            
            metric = self.metrics[operation_name]
            recent_times = list(metric['recent_times'])
            
            return {
                'operation': operation_name,
                'count': metric['count'],
                'total_time_ms': metric['total_time'],
                'avg_time_ms': metric['total_time'] / metric['count'] if metric['count'] > 0 else 0,
                'min_time_ms': metric['min_time'] if metric['min_time'] != float('inf') else 0,
                'max_time_ms': metric['max_time'],
                'recent_avg_ms': sum(recent_times) / len(recent_times) if recent_times else 0,
                'recent_count': len(recent_times)
            }
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all operations."""
        with self.lock:
            stats = {}
            for operation_name in self.metrics:
                stats[operation_name] = self.get_operation_stats(operation_name)
            
            uptime_hours = (time.time() - self.start_time) / 3600
            return {
                'uptime_hours': round(uptime_hours, 2),
                'total_operations': sum(m['count'] for m in self.metrics.values()),
                'operations': stats
            }
    
    def reset_stats(self):
        """Reset all performance statistics."""
        with self.lock:
            self.metrics.clear()
            self.start_time = time.time()


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def monitor_operation(operation_name: str):
    """Decorator to monitor function performance."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration_ms = (time.time() - start_time) * 1000
                performance_monitor.record_operation(operation_name, duration_ms)
        return wrapper
    return decorator


def get_performance_report() -> Dict[str, Any]:
    """Get a comprehensive performance report."""
    try:
        stats = performance_monitor.get_all_stats()
        
        # Add performance insights
        insights = []
        
        # Check for slow operations
        slow_operations = []
        for op_name, op_stats in stats['operations'].items():
            if op_stats['avg_time_ms'] > PERFORMANCE_LOG_THRESHOLD_MS:
                slow_operations.append({
                    'operation': op_name,
                    'avg_time_ms': op_stats['avg_time_ms'],
                    'count': op_stats['count']
                })
        
        if slow_operations:
            insights.append({
                'type': 'warning',
                'message': f"Found {len(slow_operations)} slow operations",
                'details': slow_operations
            })
        
        # Check for frequently called operations
        frequent_operations = []
        for op_name, op_stats in stats['operations'].items():
            if op_stats['count'] > 100:  # More than 100 calls
                frequent_operations.append({
                    'operation': op_name,
                    'count': op_stats['count'],
                    'avg_time_ms': op_stats['avg_time_ms']
                })
        
        if frequent_operations:
            insights.append({
                'type': 'info',
                'message': f"Found {len(frequent_operations)} frequently called operations",
                'details': frequent_operations
            })
        
        return {
            'timestamp': datetime.now().isoformat(),
            'performance_enabled': ENABLE_PERFORMANCE_MONITORING,
            'threshold_ms': PERFORMANCE_LOG_THRESHOLD_MS,
            'stats': stats,
            'insights': insights
        }
        
    except Exception as e:
        logger.error(f"Error generating performance report: {str(e)}", exc_info=True)
        return {'error': f"Failed to generate performance report: {str(e)}"}


def reset_performance_stats():
    """Reset all performance statistics."""
    try:
        performance_monitor.reset_stats()
        return {'status': 'success', 'message': 'Performance statistics reset successfully'}
    except Exception as e:
        logger.error(f"Error resetting performance stats: {str(e)}", exc_info=True)
        return {'status': 'error', 'message': f'Failed to reset performance stats: {str(e)}'}
