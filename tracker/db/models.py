from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class JiraClient(Base):
    __tablename__ = "tracker_jira_clients"

    id = Column(Integer, primary_key=True)
    url = Column(String)
    password = Column(String)
    username = Column(String)
    token = Column(String)

    user_id = Column(Integer, ForeignKey("tracker_user.id"))
    user = relationship("User")


class Toggl(Base):
    __tablename__ = "tracker_toggl"

    id = Column(Integer, primary_key=True)
    token = Column(String)
    project_id = Column(Integer)

    user_id = Column(Integer, ForeignKey("tracker_user.id"))
    user = relationship("User", back_populates="toggl")


class User(Base):
    __tablename__ = "tracker_user"

    id = Column(Integer, primary_key=True)
    tid = Column(Integer)
    rate = Column(Integer, default=5)
    total = Column(Integer, default=140)

    toggl = relationship("Toggl", back_populates="user", cascade="all, delete, delete-orphan", uselist=False)
    clients = relationship("JiraClient", back_populates="user", cascade="all, delete, delete-orphan")
