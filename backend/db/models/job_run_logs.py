from sqlalchemy import Column, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from backend.db import get_session
from backend.socket_signals import send_update
from backend.db.models.base import base

session = get_session()


class JobRunLog(base):
    __tablename__ = 'job_run_logs'

    id = Column(Integer, primary_key=True)
    job_run_id = Column(Integer, ForeignKey('job_runs.id'), nullable=False)
    job_run = relationship("JobRun", back_populates="logs")

    timestamp = Column(DateTime, nullable=False, index=True)
    message = Column(Text, nullable=False)

    def __repr__(self):
        return '<JobRunLog %r %r %r>' % (self.job_run_id, self.timestamp, self.message)

    @classmethod
    def create(cls, *args, **kwargs):
        """
        This method created specifically to emit signal to socketio.
        Please, use this method instead of default constructor
        """
        inst = cls(*args, **kwargs)
        inst._send_update()
        return inst

    def _send_update(self):
        send_update(
            'logs',
            {
                'job_id': str(instance.job_run.job.id),
                'job_run_id': str(instance.job_run.id),
                'message': instance.message,
                'timestamp': str(instance.timestamp)
            }
        )
