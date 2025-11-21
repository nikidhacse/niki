"""
Performance Monitor Module
Monitoring and analytics for system performance and usage
"""

import logging
from typing import Dict, List, Any
from dataclasses import asdict
from datetime import datetime
from data_models import PerformanceMetric

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """
    Performance Monitor: Tracks usage and performance metrics.
    
    Responsibilities:
    - Record performance metrics
    - Generate performance reports
    - Provide feedback loop for module updates
    - Track session statistics
    """
    
    def __init__(self):
        self.metrics: List[PerformanceMetric] = []
        self.session_start = datetime.now()
        self.interaction_count = 0
        self.error_count = 0
        logger.info("PerformanceMonitor: Initialized")
    
    def record_metric(self, component: str, metric_name: str, value: float) -> None:
        """
        Record a performance metric.
        
        Args:
            component: Component name (e.g., 'stt', 'intent_recognizer')
            metric_name: Metric name (e.g., 'confidence', 'latency')
            value: Metric value
        """
        metric = PerformanceMetric(
            component=component,
            metric_name=metric_name,
            value=value
        )
        self.metrics.append(metric)
        logger.debug(f"PerformanceMonitor: Recorded {component}.{metric_name} = {value}")
    
    def record_interaction(self, success: bool = True) -> None:
        """Record an interaction"""
        self.interaction_count += 1
        if not success:
            self.error_count += 1
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get summary of recorded metrics.
        
        Returns:
            Dict: Summary including averages and statistics
        """
        if not self.metrics:
            return {
                "message": "No metrics recorded",
                "interaction_count": self.interaction_count,
                "error_count": self.error_count,
                "session_duration": (datetime.now() - self.session_start).total_seconds()
            }
        
        summary = {}
        for metric in self.metrics:
            key = f"{metric.component}.{metric.metric_name}"
            if key not in summary:
                summary[key] = []
            summary[key].append(metric.value)
        
        # Calculate statistics
        statistics = {}
        for key, values in summary.items():
            statistics[key] = {
                "count": len(values),
                "average": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "total": sum(values)
            }
        
        session_duration = (datetime.now() - self.session_start).total_seconds()
        
        return {
            "total_metrics": len(self.metrics),
            "total_interactions": self.interaction_count,
            "total_errors": self.error_count,
            "error_rate": self.error_count / self.interaction_count if self.interaction_count > 0 else 0,
            "session_duration_seconds": session_duration,
            "statistics": statistics,
            "recent_metrics": [asdict(m) for m in self.metrics[-10:]]
        }
    
    def get_feedback_report(self) -> Dict[str, Any]:
        """
        Generate feedback for module updates based on collected metrics.
        
        Returns:
            Dict: Feedback report with recommendations
        """
        summary = self.get_metrics_summary()
        recommendations = []
        
        # Analyze metrics and provide recommendations
        if summary.get("error_rate", 0) > 0.1:
            recommendations.append("High error rate detected: Review module implementations")
        
        if "intent_recognizer.confidence" in summary.get("statistics", {}):
            avg_confidence = summary["statistics"]["intent_recognizer.confidence"]["average"]
            if avg_confidence < 0.7:
                recommendations.append("Low intent recognition confidence: Consider retraining NLU model")
        
        if "stt.confidence" in summary.get("statistics", {}):
            avg_stt_confidence = summary["statistics"]["stt.confidence"]["average"]
            if avg_stt_confidence < 0.8:
                recommendations.append("Low STT confidence: Optimize speech-to-text settings")
        
        if not recommendations:
            recommendations.append("System performance is good. Continue monitoring.")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "session_duration": summary.get("session_duration_seconds"),
            "total_interactions": summary.get("total_interactions"),
            "error_rate": summary.get("error_rate"),
            "performance_data": summary,
            "recommendations": recommendations
        }
    
    def reset_session(self) -> None:
        """Reset session metrics"""
        self.metrics.clear()
        self.session_start = datetime.now()
        self.interaction_count = 0
        self.error_count = 0
        logger.info("PerformanceMonitor: Session reset")
    
    def export_metrics(self) -> List[Dict[str, Any]]:
        """
        Export all metrics as dictionaries.
        
        Returns:
            List[Dict]: All recorded metrics as dicts
        """
        return [asdict(metric) for metric in self.metrics]
    
    def get_metric_history(self, component: str, metric_name: str) -> List[float]:
        """
        Get history of a specific metric.
        
        Args:
            component: Component name
            metric_name: Metric name
            
        Returns:
            List[float]: History of metric values
        """
        return [
            m.value for m in self.metrics
            if m.component == component and m.metric_name == metric_name
        ]
