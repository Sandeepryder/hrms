# utils/orm_utils.py
from datetime import datetime

def sqlalchemy_obj_to_dict(obj):
    """
    Simple serializer: converts SQLAlchemy model instance to dict (columns only).
    """
    data = {}
    for col in obj.__table__.columns:
        val = getattr(obj, col.name)
        if isinstance(val, datetime):
            data[col.name] = val.isoformat()
        else:
            data[col.name] = val
    return data
