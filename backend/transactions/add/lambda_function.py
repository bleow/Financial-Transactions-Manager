import hashlib
import re
import uuid
from currency_converter import CurrencyConverter
from flask.app import Flask
from flask.globals import request
from flask_cors.extension import CORS

app = Flask(__name__)
cors = CORS(app)

from backend.transactions.add.database import UserCard, CardType, Decorator, UnprocessedTransactions, get_session


def get_hash(string: str):
    return hashlib.sha256(string.encode("utf-8")).hexdigest()


@app.route('/', methods=['POST'])
def lambda_handler():
    db = get_session()
    data = request.json
    print("data is", data)
    # validate compulsory fields
    try:
        data['mcc'] = int(data['mcc'])
    except ValueError:
        return f'MCC {data["mcc"]} must be be a positive number.'

    try:
        data['amount'] = float(data['amount'])
    except ValueError:
        return f'Amount {data["amount"]} must be a positive number.'

    if not re.match('\d{4}-\d{2}-\d{2}', data['transaction_date']):
        return f'Transaction date {data["transaction_date"]} must be a valid date.'

    card_pan = re.sub('[^0-9]', '', str(data['card_pan']))
    if not 13 <= len(card_pan) <= 19:
        return f'Card PAN {data["card_pan"]} must be 13-19 digits long.'

    res = db.query(UserCard).filter(UserCard.card_pan_hash == get_hash(card_pan)).first()
    try:
        res = res.as_dict()
    except AttributeError:
        return f'No transaction with card pan {card_pan}.'

    # validate optional fields
    if 'card_type' in data:
        if data['card_type'] not in [i.name for i in CardType]:
            return f'Card Type {data["card_type"]} is invalid.'
        if str(data['card_type']) != str(res['card_type'].name):
            return f'Card Type {data["card_type"]} does not match the the card PAN provided'
    data['card_type'] = str(res['card_type'].name)

    # add internal fields
    data['user_id'] = res['user_id']

    is_foreign = data['currency'] == 'SGD'
    is_hotel = 3500 <= int(data['mcc']) <= 3999
    is_online = 5815 <= int(data['mcc']) <= 5818
    total_active = sum([is_foreign, is_hotel, is_online])
    res2 = db.query(Decorator).where((Decorator.total_active == total_active) &
                                     (Decorator.is_foreign == is_foreign) &
                                     (Decorator.is_hotel == is_hotel) &
                                     (Decorator.is_online == is_online)).first().as_dict()
    data['decorator_id'] = res2['decorator_id']

    c = CurrencyConverter()
    data['amount'] = c.convert(data['amount'], data['currency'], 'SGD')

    try:
        db.add(
            UnprocessedTransactions(transaction_id=uuid.uuid4(), merchant=data['merchant'],
                                    mcc=data['mcc'], amount=data['amount'], transaction_date=data['transaction_date'],
                                    card_type=data['card_type'], user_id=data['user_id'],
                                    decorator_id=data['decorator_id']))
    except ValueError:
        return f'{data["transaction_id"]}: An error occurred while attempting database storage.'

    db.commit()
    return "Success"


if __name__ == "__main__":
    app.run(port=8080)