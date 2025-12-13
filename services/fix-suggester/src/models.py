from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum
from datetime import datetime
import enum
from .database import Base

class SeverityLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class VulnerabilityType(str, enum.Enum):
    UNPINNED_ACTION = "unpinned_action"
    EXCESSIVE_PERMISSIONS = "excessive_permissions"
    HARDCODED_SECRET = "hardcoded_secret"
    WEAK_HARDENING = "weak_hardening"

class FixSuggestion(Base):
    __tablename__ = "fix_suggestions"

    id = Column(Integer, primary_key=True, index=True)
    vulnerability_type = Column(String(100), nullable=False)
    original_yaml = Column(Text, nullable=False)
    fixed_yaml = Column(Text, nullable=False)
    diff = Column(Text, nullable=False)
    description = Column(Text)
    severity = Column(String(20), nullable=False)
    auto_applicable = Column(String(10), default="true")
    timestamp = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<FixSuggestion(id={self.id}, type={self.vulnerability_type}, severity={self.severity})>"
