import json
from database import get_session
from getTransactionByCard import get_transaction_by_card

def lambda_handler(event, context):
    # TODO implement
    try:
        response = get_transaction_by_card(db=get_session(), card_type=event["cardType"], user_id=event["userId"], page=int(event["page"]))
        return response
    except Exception as e:
        print(e)

    return False