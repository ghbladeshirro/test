from datetime import datetime, time
from sqlalchemy import (
    Column, Integer, String, Time, ForeignKey, 
    CheckConstraint, UniqueConstraint, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func

Base = declarative_base()


class Group(Base):
    __tablename__ = 'groups'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    course = Column(Integer, nullable=False)
    
    schedule = relationship("Schedule", back_populates="group")


class Teacher(Base):
    __tablename__ = 'teachers'
    
    id = Column(Integer, primary_key=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(100), unique=True)
    
    schedule = relationship("Schedule", back_populates="teacher")


class Classroom(Base):
    __tablename__ = 'classrooms'
    
    id = Column(Integer, primary_key=True)
    building = Column(String(50), nullable=False)
    room_number = Column(String(10), nullable=False)
    capacity = Column(Integer, nullable=False)
    
    schedule = relationship("Schedule", back_populates="classroom")
    
    __table_args__ = (
        UniqueConstraint('building', 'room_number'),
    )


class Course(Base):
    __tablename__ = 'courses'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    hours_total = Column(Integer, nullable=False)
    
    schedule = relationship("Schedule", back_populates="course")


class Schedule(Base):
    __tablename__ = 'schedule_items'
    
    id = Column(Integer, primary_key=True)
    
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    teacher_id = Column(Integer, ForeignKey('teachers.id'), nullable=False)
    classroom_id = Column(Integer, ForeignKey('classrooms.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    
    day_of_week = Column(Integer, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    
    semester = Column(String(20), nullable=False)
    
    created_at = Column(DateTime, default=func.now())
    
    group = relationship("Group", back_populates="schedule")
    teacher = relationship("Teacher", back_populates="schedule")
    classroom = relationship("Classroom", back_populates="schedule")
    course = relationship("Course", back_populates="schedule")
    
    __table_args__ = (
        CheckConstraint('day_of_week BETWEEN 1 AND 7'),
        CheckConstraint('start_time < end_time'),
        
        UniqueConstraint('classroom_id', 'day_of_week', 'start_time', 'semester', 
                        name='uq_classroom_time'),
        UniqueConstraint('teacher_id', 'day_of_week', 'start_time', 'semester',
                        name='uq_teacher_time'),
        UniqueConstraint('group_id', 'day_of_week', 'start_time', 'semester',
                        name='uq_group_time'),
    )


engine = create_engine('sqlite:///schedule.db')
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)