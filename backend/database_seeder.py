import uuid

from backend.transactions.add_bulk.database import Exclusions, Decorator, UserCard, CardType, RewardType, User
from backend.transactions.add_bulk.database import get_session

import hashlib


def get_hash(string: str):
    return hashlib.sha256(string.encode("utf-8")).hexdigest()


def seed_db(db):
    db.add(Exclusions(mcc=6051, reward_type=RewardType(1)))
    db.add(Exclusions(mcc=6051, reward_type=RewardType(2)))
    db.add(Exclusions(mcc=9399, reward_type=RewardType(1)))
    db.add(Exclusions(mcc=9399, reward_type=RewardType(2)))
    db.add(Exclusions(mcc=6540, reward_type=RewardType(1)))
    db.add(Exclusions(mcc=6540, reward_type=RewardType(2)))

    db.add(Decorator(total_active=0))
    db.add(Decorator(total_active=1, is_online=1))
    db.add(Decorator(total_active=1, is_foreign=1))
    db.add(Decorator(total_active=1, is_hotel=1))
    db.add(Decorator(total_active=2, is_online=1, is_foreign=1))
    db.add(Decorator(total_active=2, is_online=1, is_hotel=1))
    db.add(Decorator(total_active=2, is_foreign=1, is_hotel=1))
    db.add(Decorator(total_active=3, is_online=1, is_foreign=1, is_hotel=1))

    import boto3
    import pandas as pd
    from io import StringIO
    import regex as re

    # client = boto3.client('s3')
    # bucket_name = 'databaseseeding'
    # object_key = 'users.csv'
    # csv_obj = client.get_object(Bucket=bucket_name, Key=object_key)
    # body = csv_obj['Body']
    # csv_string = body.read().decode('utf-8')
    # df = pd.read_csv(StringIO(csv_string))
    #
    # users = {}
    # for row_dict in df.to_dict(orient="records"):
    #     print(row_dict)
    #     card_pan = str(re.sub('[^0-9]', '', row_dict['card_pan']))
    #     card_pan_hash = get_hash(card_pan)
    #     card_pan_last = int(card_pan[-4:])
    #     card_type = row_dict['card_type']
    #     user_id = uuid.uuid4()
    #     db.add(UserCard(card_pan_hash=card_pan_hash, card_pan_last=card_pan_last, card_type=card_type,
    #                     user_id=user_id))
    # for k, v in users.items():
    #     db.add(User(user_id=k, email=v))
    #
    # client2 = boto3.client('s3')
    # bucket_name2 = 'batchuploadbucket'
    # object_key2 = 'public/Project B (Appendix 2a) - spend.first.1000.csv'
    # csv_obj2 = client2.get_object(Bucket=bucket_name2, Key=object_key2)
    # body2 = csv_obj2['Body']
    # csv_string2 = body2.read().decode('utf-8')
    # df2 = pd.read_csv(StringIO(csv_string2))
    df2 = pd.read_csv("spend.csv", header=0)

    card_seeder = {}
    for row_dict in df2.to_dict(orient="records"):
        card_pan = re.sub('[^0-9]', '', row_dict['card_pan'])
        if get_hash(card_pan) not in card_seeder:
            card_seeder[get_hash(card_pan)] = [int(card_pan[-4:]), row_dict['card_type']]
    for k, v in card_seeder.items():
        user_id = uuid.uuid4()
        db.add(User(user_id=user_id, email='RabbakUser@gmail.com'))
        db.add(UserCard(card_pan_hash=k, user_id=user_id, card_pan_last=v[0], card_type=v[1]))

    db.commit()

if __name__ == "__main__":
    db = get_session()
    seed_db(db)
