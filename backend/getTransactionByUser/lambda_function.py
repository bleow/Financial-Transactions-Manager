import json
from database import get_session
from getTransactionsByUser import get_transactions_by_user

def lambda_handler(event, context):
    # TODO implement
    try:
        response = get_transactions_by_user(db=get_session(), user_id=event["userId"], page=int(event["page"]))
        return response
    except Exception as e:
        print(e)

    return False