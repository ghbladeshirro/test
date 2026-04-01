from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from requests import get_user_orders_with_total, get_user_orders_with_details

DATABASE_URL = "postgresql://user:password@localhost/dbname"
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

user_id = 1

orders = get_user_orders_with_total(session, user_id)

print(f"Заказы пользователя {user_id}:")
for order in orders:
    print(f"Заказ #{order.id}: Дата: {order.order_date}, Статус: {order.status}, Сумма: {order.total_sum}")

detailed_orders = get_user_orders_with_details(session, user_id)

print(f"\nДетализация заказов:")
for item in detailed_orders:
    print(f"Заказ #{item.order_id}: {item.product_name} x{item.quantity} = {item.item_total}")

session.close()