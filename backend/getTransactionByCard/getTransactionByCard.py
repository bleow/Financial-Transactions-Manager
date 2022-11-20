from sqlalchemy import delete, and_
from database import ProcessedTransactions as Transaction
import json
import uuid


def get_transaction_by_card(db, card_type, user_id, page):
    page_len = 10
    try:
        transactions = db.query(Transaction).filter(and_((Transaction.card_type == card_type), (Transaction.user_id == uuid.UUID(user_id)))).order_by(Transaction.transaction_date.desc()).slice((page - 1) * page_len, (page - 1) * page_len + page_len).all()
        
        result = []
        for transactionObj in transactions:
            transaction = transactionObj.as_dict()
            transaction['transaction_id'] = str(transaction['transaction_id'])
            transaction['transaction_date'] = str(transaction['transaction_date'])
            transaction['user_id'] = str(transaction['user_id'])
            transaction['card_type'] = str(transaction['card_type'].name)
            result.append(transaction)
            
        return result
        
    except Exception as err:
        db.rollback()
        print(err)
        raise err