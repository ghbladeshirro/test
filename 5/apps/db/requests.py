from pydantic import BaseModel, validator
from datetime import time, date
from typing import Optional, List


class ScheduleCreate(BaseModel):
    """Создание занятия"""
    group_id: int
    teacher_id: int
    classroom_id: int
    course_id: int
    day_of_week: int  # 1-7
    start_time: time
    end_time: time
    semester: str
    
    @validator('day_of_week')
    def validate_day(cls, v):
        if not 1 <= v <= 7:
            raise ValueError('day_of_week должен быть от 1 до 7')
        return v
    
    @validator('end_time')
    def validate_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time должен быть после start_time')
        return v


class ScheduleResponse(BaseModel):
    """Ответ с данными занятия"""
    id: int
    group_id: int
    group_name: str
    teacher_id: int
    teacher_name: str
    classroom_id: int
    classroom_name: str
    course_id: int
    course_title: str
    day_of_week: int
    start_time: time
    end_time: time
    semester: str
    
    class Config:
        orm_mode = True


class ConflictResponse(BaseModel):
    """Ответ о конфликте"""
    has_conflict: bool
    conflicts: List[str]