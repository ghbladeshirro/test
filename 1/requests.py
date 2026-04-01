from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Order, OrderItem, Product

def get_user_orders_with_total(session: Session, user_id: int):
    orders_with_totals = session.query(
        Order.id,
        Order.order_date,
        Order.status,
        func.coalesce(func.sum(OrderItem.quantity * OrderItem.price_at_moment), 0).label('total_sum')
    ).outerjoin(
        OrderItem, Order.id == OrderItem.order_id
    ).filter(
        Order.user_id == user_id
    ).group_by(
        Order.id
    ).all()
    
    return orders_with_totals


def get_user_orders_with_details(session: Session, user_id: int):
    result = session.query(
        Order.id.label('order_id'),
        Order.order_date,
        Order.status,
        Product.name.label('product_name'),
        OrderItem.quantity,
        OrderItem.price_at_moment,
        (OrderItem.quantity * OrderItem.price_at_moment).label('item_total')
    ).join(
        OrderItem, Order.id == OrderItem.order_id
    ).join(
        Product, OrderItem.product_id == Product.id
    ).filter(
        Order.user_id == user_id
    ).order_by(
        Order.order_date.desc()
    ).all()
    
    return result