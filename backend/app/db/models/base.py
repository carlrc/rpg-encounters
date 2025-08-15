from sqlalchemy.orm import DeclarativeBase


# Unified base for models that need both memory and reveal relationships
class UnifiedBase(DeclarativeBase):
    pass
