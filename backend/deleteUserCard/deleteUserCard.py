from sqlalchemy import delete, and_
from database import UserCard, User
import uuid
from sqlalchemy.dialects.postgresql import UUID

# def delete_user_card(db, user_id, card_id):
#     try:
#         user = db.query(User_To_Card).filter(and_((User_To_Card.Card_ID == card_id), (User_To_Card.User_ID == user_id))).one()
#         db.delete(user)
#         db.commit()
#         return True
        
#     except Exception as err:
#         db.rollback()
#         raise err
        
# def delete_user(db, user_id):
#     try:
#         user = db.query(User).filter(User.user_id == user_id).one()
#         db.delete(user)
#         db.commit()
#         return f'user with user_id {user_id} deleted'
        
#     except Exception as err:
#         db.rollback()
#         raise err

def create_user(db):
    try:

        new = User(user=str(uuid.uuid4()), total_points=0, total_miles=0, total_cashback=0, email="rabbak@gmail.com")
        db.add(new)
        db.commit()
        return "done"
    except Exception as err:
        return "gg" + err
        