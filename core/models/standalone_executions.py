import datetime
import enum

from sqlalchemy import Column, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from core.models.base import base


class StandaloneExecution(base):
    pass
