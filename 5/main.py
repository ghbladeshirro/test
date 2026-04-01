from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from apps.db.models import (
    Group, Teacher, Classroom, Course, Schedule,
    SessionLocal, init_db
)
from requests import ScheduleCreate, ScheduleResponse, ConflictResponse

app = FastAPI(title="Расписание занятий")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def startup():
    """При запуске создаем таблицы"""
    init_db()


def check_conflicts(db: Session, schedule: ScheduleCreate, exclude_id: int = None):
    """
    Проверка конфликтов:
    1. Аудитория занята
    2. Преподаватель занят
    3. Группа занята
    """
    conflicts = []
    
    def base_query(field):
        q = db.query(Schedule).filter(
            field == getattr(schedule, field.key),
            Schedule.day_of_week == schedule.day_of_week,
            Schedule.semester == schedule.semester,
            Schedule.start_time < schedule.end_time,
            Schedule.end_time > schedule.start_time
        )
        if exclude_id:
            q = q.filter(Schedule.id != exclude_id)
        return q
    
    # проверка аудитории
    classroom_conflict = base_query(Schedule.classroom_id).first()
    if classroom_conflict:
        conflicts.append(
            f"Аудитория {classroom_conflict.classroom.building}-{classroom_conflict.classroom.room_number} "
            f"занята с {classroom_conflict.start_time} до {classroom_conflict.end_time}"
        )
    
    # проверка преподавателя
    teacher_conflict = base_query(Schedule.teacher_id).first()
    if teacher_conflict:
        conflicts.append(
            f"Преподаватель {teacher_conflict.teacher.full_name} "
            f"занят с {teacher_conflict.start_time} до {teacher_conflict.end_time}"
        )
    
    # проверка группы
    group_conflict = base_query(Schedule.group_id).first()
    if group_conflict:
        conflicts.append(
            f"Группа {group_conflict.group.name} "
            f"занята с {group_conflict.start_time} до {group_conflict.end_time}"
        )
    
    return conflicts


@app.post("/api/schedule", response_model=ScheduleResponse)
def create_schedule(schedule: ScheduleCreate, db: Session = Depends(get_db)):
    """Создание занятия"""
    
    # проверка на существование записей
    group = db.query(Group).filter(Group.id == schedule.group_id).first()
    teacher = db.query(Teacher).filter(Teacher.id == schedule.teacher_id).first()
    classroom = db.query(Classroom).filter(Classroom.id == schedule.classroom_id).first()
    course = db.query(Course).filter(Course.id == schedule.course_id).first()
    
    if not all([group, teacher, classroom, course]):
        raise HTTPException(404, "Не найдена одна из сущностей")
    
    # проверка на конфликты
    conflicts = check_conflicts(db, schedule)
    if conflicts:
        raise HTTPException(409, {"message": "Конфликт расписания", "conflicts": conflicts})
    
    # создание занятия
    new_schedule = Schedule(
        group_id=schedule.group_id,
        teacher_id=schedule.teacher_id,
        classroom_id=schedule.classroom_id,
        course_id=schedule.course_id,
        day_of_week=schedule.day_of_week,
        start_time=schedule.start_time,
        end_time=schedule.end_time,
        semester=schedule.semester
    )
    
    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)
    
    # вывод текста
    return ScheduleResponse(
        id=new_schedule.id,
        group_id=group.id,
        group_name=group.name,
        teacher_id=teacher.id,
        teacher_name=teacher.full_name,
        classroom_id=classroom.id,
        classroom_name=f"{classroom.building}-{classroom.room_number}",
        course_id=course.id,
        course_title=course.title,
        day_of_week=new_schedule.day_of_week,
        start_time=new_schedule.start_time,
        end_time=new_schedule.end_time,
        semester=new_schedule.semester
    )


@app.get("/api/schedule/check", response_model=ConflictResponse)
def check_schedule_conflicts(schedule: ScheduleCreate,db: Session = Depends(get_db)):
    """Проверка конфликтов без сохранения"""
    conflicts = check_conflicts(db, schedule)
    return ConflictResponse(
        has_conflict=len(conflicts) > 0,
        conflicts=conflicts
    )


@app.get("/api/schedule/group/{group_id}", response_model=List[ScheduleResponse])
def get_group_schedule(group_id: int, semester: str = None, db: Session = Depends(get_db)):
    """Расписание группы"""
    query = db.query(Schedule).filter(Schedule.group_id == group_id)
    if semester:
        query = query.filter(Schedule.semester == semester)
    
    schedules = query.order_by(Schedule.day_of_week, Schedule.start_time).all()
    
    result = []
    for s in schedules:
        result.append(ScheduleResponse(
            id=s.id,
            group_id=s.group.id,
            group_name=s.group.name,
            teacher_id=s.teacher.id,
            teacher_name=s.teacher.full_name,
            classroom_id=s.classroom.id,
            classroom_name=f"{s.classroom.building}-{s.classroom.room_number}",
            course_id=s.course.id,
            course_title=s.course.title,
            day_of_week=s.day_of_week,
            start_time=s.start_time,
            end_time=s.end_time,
            semester=s.semester
        ))
    
    return result


@app.get("/api/schedule/teacher/{teacher_id}", response_model=List[ScheduleResponse])
def get_teacher_schedule(teacher_id: int, semester: str = None,db: Session = Depends(get_db)):
    """Расписание преподавателя"""
    query = db.query(Schedule).filter(Schedule.teacher_id == teacher_id)
    if semester:
        query = query.filter(Schedule.semester == semester)
    
    schedules = query.order_by(Schedule.day_of_week, Schedule.start_time).all()
    
    result = []
    for s in schedules:
        result.append(ScheduleResponse(
            id=s.id,
            group_id=s.group.id,
            group_name=s.group.name,
            teacher_id=s.teacher.id,
            teacher_name=s.teacher.full_name,
            classroom_id=s.classroom.id,
            classroom_name=f"{s.classroom.building}-{s.classroom.room_number}",
            course_id=s.course.id,
            course_title=s.course.title,
            day_of_week=s.day_of_week,
            start_time=s.start_time,
            end_time=s.end_time,
            semester=s.semester
        ))
    
    return result


@app.delete("/api/schedule/{schedule_id}")
def delete_schedule(schedule_id: int,db: Session = Depends(get_db)):
    """Удаление занятия"""
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(404, "Занятие не найдено")
    
    db.delete(schedule)
    db.commit()
    
    return {"message": "Занятие удалено"}


# примеры
@app.post("/api/test-data")
def create_test_data(db: Session = Depends(get_db)):
    """Создание тестовых данных"""
    
    # создание группы
    group1 = Group(name="ПИ-201", course=2)
    group2 = Group(name="ПИ-202", course=2)
    db.add_all([group1, group2])
    
    # создание преподавателей
    teacher1 = Teacher(full_name="Иванов Иван Иванович", email="ivanov@university.ru")
    teacher2 = Teacher(full_name="Белов Димасик Сергеевич ", email="petrova@university.ru")
    db.add_all([teacher1, teacher2])
    
    # слздание аудитории
    classroom1 = Classroom(building="Главный", room_number="301", capacity=50)
    classroom2 = Classroom(building="Главный", room_number="302", capacity=40)
    db.add_all([classroom1, classroom2])
    
    # слздание курса
    course1 = Course(title="Базы данных", hours_total=72)
    course2 = Course(title="Python программирование", hours_total=64)
    db.add_all([course1, course2])
    
    db.commit()
    
    return {"message": "Тестовые данные созданы"}