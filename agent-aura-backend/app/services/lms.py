from abc import ABC, abstractmethod
from typing import Dict, Any, List
import random
from datetime import datetime, timedelta

class LMSProvider(ABC):
    """Abstract base class for LMS providers."""
    
    @abstractmethod
    def get_student_data(self, student_id: str) -> Dict[str, Any]:
        """Fetch student data from the LMS."""
        pass

    @abstractmethod
    def get_assignments(self, student_id: str) -> List[Dict[str, Any]]:
        """Fetch recent assignments."""
        pass

class CanvasProvider(LMSProvider):
    """Mock provider for Canvas LMS."""
    
    def get_student_data(self, student_id: str) -> Dict[str, Any]:
        # Mock data for Canvas
        return {
            "source": "Canvas LMS",
            "last_login": (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat(),
            "course_participation": f"{random.randint(70, 100)}%",
            "missing_assignments": random.randint(0, 3)
        }

    def get_assignments(self, student_id: str) -> List[Dict[str, Any]]:
        return [
            {"id": "101", "name": "Math Quiz 3", "status": "submitted", "score": 85},
            {"id": "102", "name": "History Essay", "status": "missing", "score": None}
        ]

class GoogleClassroomProvider(LMSProvider):
    """Mock provider for Google Classroom."""
    
    def get_student_data(self, student_id: str) -> Dict[str, Any]:
        # Mock data for Google Classroom
        return {
            "source": "Google Classroom",
            "active_courses": 5,
            "stream_posts": random.randint(2, 10),
            "turned_in_rate": f"{random.randint(80, 100)}%"
        }

    def get_assignments(self, student_id: str) -> List[Dict[str, Any]]:
        return [
            {"id": "201", "name": "Science Lab Report", "status": "turned_in", "grade": "B+"},
            {"id": "202", "name": "Art Project", "status": "assigned", "grade": None}
        ]

class LMSFactory:
    """Factory to get LMS provider instances."""
    
    @staticmethod
    def get_provider(platform: str) -> LMSProvider:
        if platform.lower() == "canvas":
            return CanvasProvider()
        elif platform.lower() == "google_classroom":
            return GoogleClassroomProvider()
        else:
            raise ValueError(f"Unsupported LMS platform: {platform}")
