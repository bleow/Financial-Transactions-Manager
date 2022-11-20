import csv
import json
import os
import time
import boto3
import botocore.response
import re
import hashlib
import enum
import uuid
from sqlalchemy import create_engine, ForeignKey, BIGINT, TypeDecorator, CHAR, Enum, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Boolean
from currency_converter import CurrencyConverter
import urllib.parse 

pw = "11111111"
DATABASE_URL = "mysql+pymysql://admin:" + pw + "@database-1-instance-1.cqbbxkouucyk.us-east-1.rds.amazonaws.com:3306/cs301_scis_bank"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_session():
    """ Creates a db session """
    try:
        _db = SessionLocal()
        return _db
    finally:
        _db.close()

class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses Postgresql's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    https://docs.sqlalchemy.org/en/14/core/custom_types.html?highlight=uuid#backend-agnostic-guid-type
    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(64))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            else:
                # hexstring
                return value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)


class CardType(enum.Enum):
    scis_platinummiles = 1
    scis_shopping = 2
    scis_freedom = 3
    scis_premiummiles = 4


class RewardType(enum.Enum):
    Points = 1
    Miles = 2
    Cashback = 3


class EarnType(enum.Enum):
    BER = 1
    AC = 2
    CPM = 3


class Decorator(Base):
    """
    A special table storing the special 'decorator' attributes of a Transaction and Exclusion
    """
    __tablename__ = 'decorator'
    decorator_id = Column(Integer, primary_key=True)
    total_active = Column(Integer)
    is_foreign = Column(Boolean, default=0)
    is_online = Column(Boolean, default=0)
    is_hotel = Column(Boolean, default=0)
    transaction = relationship("UnprocessedTransactions", cascade="all, delete")
    rewardsprogram = relationship("RewardsProgram", cascade="all, delete")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class User(Base):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}
    user_id = Column(GUID, primary_key=True)
    total_points = Column(Integer, nullable=False, default=0)
    total_miles = Column(Integer, nullable=False, default=0)
    total_cashback = Column(Integer, nullable=False, default=0)
    email = Column(String(255), nullable=False)
    usercard = relationship("UserCard", cascade="all, delete")


class UserCard(Base):
    """
    Our user table storing the users and their cards
    """
    __tablename__ = 'usercard'
    __table_args__ = {'extend_existing': True}
    card_pan_hash = Column(String(255), primary_key=True)
    card_pan_last = Column(Integer, nullable=False)
    card_type = Column(Enum(CardType), nullable=False)
    user_id = Column(GUID, ForeignKey("user.user_id"))

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class UnprocessedTransactions(Base):
    """
    Transactions received from user and processed before storing.
    """
    __tablename__ = 'unprocessedtransaction'
    __table_args__ = {'extend_existing': True}
    transaction_id = Column(GUID, primary_key=True)
    merchant = Column(String(255), nullable=False)
    mcc = Column(Integer, nullable=True)
    amount = Column(Float, nullable=False)
    transaction_date: datetime = Column(DateTime, nullable=False)
    # Optional fields. If supplied we will validate regardless
    card_type = Column(Enum(CardType))
    # Internal fields. We add them on our own
    user_id = Column(GUID)
    decorator_id = Column(Integer, ForeignKey("decorator.decorator_id"))

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Exclusions(Base):
    """
    MCC (from rewards)
    """
    __tablename__ = 'exclusions'
    __table_args__ = {'extend_existing': True}
    mcc = Column(Integer, primary_key=True)
    reward_type = Column(Enum(RewardType), primary_key=True)


class RewardsProgram(Base):
    """
    Base Earn rate	                       Applicable Categories
    1 point/SGD on spend*
    4 points/SGD on all shopping spend	    10 points/SGD on all online spend
    """
    __tablename__ = 'rewardsprogram'
    __table_args__ = {'extend_existing': True}
    rewards_program_id = Column(GUID, primary_key=True)
    card_type = Column(Enum(CardType), nullable=False)
    reward_type = Column(Enum(RewardType), nullable=False)
    earn_type = Column(Enum(EarnType), nullable=False)
    amount = Column(BIGINT, nullable=False)
    min_spend = Column(BIGINT, nullable=False)
    is_stackable = Column(Boolean, nullable=False)
    campaign = relationship("Campaign", cascade="all, delete")
    decorator_id = Column(Integer, ForeignKey("decorator.decorator_id"), nullable=False)


class Campaign(Base):
    """
    4 miles per dollar with Grab, min spend 100 SGD
    """
    __tablename__ = 'campaign'
    __table_args__ = {'extend_existing': True}
    merchant = Column(String(255))
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    description = Column(String(255))
    rewards_program_id = Column(GUID, ForeignKey("rewardsprogram.rewards_program_id"), primary_key=True)


class ProcessedTransactions(Base):
    """
    Transactions to process to give out rewards
    """
    __tablename__ = 'processedtransaction'
    __table_args__ = {'extend_existing': True}
    transaction_id = Column(GUID, primary_key=True)
    merchant = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    transaction_date = Column(DateTime, nullable=False)
    card_type = Column(Enum(CardType))
    rewards = Column(Integer)
    user_id = Column(GUID)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


Base.metadata.create_all(engine)


def get_hash(string: str):
    return hashlib.sha256(string.encode("utf-8")).hexdigest()
    

s3_resource = boto3.resource('s3')
client = boto3.client('lambda')
# 5 seconds minimum before function stops
MINIMUN_REMAINING_TIME_MS = 5000

def lambda_handler(event, context):
    # read event
    ## if event comes from s3, offset = 0
    offset = event.get('offset', 0)
    bucket_name2 = event['Records'][0]['s3']['bucket']['name'] #'batchuploadbucket'
    object_key2 = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8') #'public/Project B (Appendix 2a) - spend.first.1000.csv'
    
    s3_object = s3_resource.Object(bucket_name=bucket_name2, key=object_key2)
    bodylines = get_object_bodylines(s3_object, offset)
    fieldnames = event.get('fieldnames', None)
    
    msg = []
    
    csv_reader = csv.DictReader(bodylines.iter_lines(), fieldnames=fieldnames)
    db = get_session()
    
    i=0
    total = 0
    for row in csv_reader:
        total+=1
        # print(row)
        data = row 
        
        ######################## PROCESSING

        # validate compulsory fields
        try:
            data['mcc'] = int(data['mcc'])
        except ValueError:
            msg.append({data['transaction_id']: f'MCC {data["mcc"]} must be be a positive number.'})
            continue
    
        try:
            data['amount'] = float(data['amount'])
        except ValueError:
            msg.append({data['transaction_id']: f'Amount {data["amount"]} must be a positive number.'})
            continue
    
        if not re.match('\d{4}-\d{2}-\d{2}', data['transaction_date']):
            msg.append({data['transaction_id']: f'Transaction date {data["transaction_date"]} must be a valid date.'})
            continue
    
        card_pan = re.sub('[^0-9]', '', str(data['card_pan']))
        if not 13 <= len(card_pan) <= 19:
            msg.append({data['transaction_id']: f'Card PAN {data["card_pan"]} must be 13-19 digits long.'})
            continue
    
        res = db.query(UserCard).filter(UserCard.card_pan_hash == get_hash(card_pan)).first()
        try:
            res = res.as_dict()
        except AttributeError:
            msg.append(f'No transaction with card pan {card_pan}.')
            continue
        
        # validate optional fields
        if 'card_type' in data:
            if data['card_type'] not in [i.name for i in CardType]:
                msg.append({data['transaction_id']: f'Card Type {data["card_type"]} is invalid.'})
                continue
            if str(data['card_type']) != str(res['card_type'].name):
                msg.append({data['transaction_id']: 'Card Type provided does not match the the card PAN provided'})
                continue
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
    
        db.add(
            UnprocessedTransactions(transaction_id=uuid.uuid4(), merchant=data['merchant'],
                                    mcc=data['mcc'], amount=data['amount'], transaction_date=data['transaction_date'],
                                    card_type=data['card_type'], user_id=data['user_id'],
                                    decorator_id=data['decorator_id']))
        db.commit()
        # print('COMMITING DATA', data)
    
        
        
        ########################
        
        #just for verbose
        if i % 100 == 0:
            print('remaining_time is:', context.get_remaining_time_in_millis())
            print(f'row_number:{i}', row)
            #sleep for testing on small file, WARNING: sleep seems to break the streaming, causing it to start from the starting offset
            # time.sleep(2)
        i +=1
        if context.get_remaining_time_in_millis() < MINIMUN_REMAINING_TIME_MS:
            fieldnames = fieldnames or csv_reader.fieldnames
            new_offset = offset + bodylines.offset
            print('new_offset',new_offset)
            if new_offset < s3_object.content_length:
                
                new_event = {
                    **event,
                    "offset": new_offset,
                    "fieldnames": fieldnames
                }
                print(new_event)
                invoke_lambda(context.function_name, new_event)
            break
            

        # print(total)
    return total

def invoke_lambda(function_name, event):
    payload = json.dumps(event).encode('utf-8')
    function_name = 'test_recursive_hell'
    response = client.invoke(
        FunctionName=function_name,
        InvocationType='Event',
        Payload=payload
    )


def get_object_bodylines(s3_object, offset):
    resp = s3_object.get(Range=f'bytes={offset}-')
    body: botocore.response.StreamingBody = resp['Body']
    return BodyLines(body)


class BodyLines:
    def __init__(self, body: botocore.response.StreamingBody, initial_offset=0):
        self.body = body
        self.offset = initial_offset

    def iter_lines(self, chunk_size=1024):
        """Return an iterator to yield lines from the raw stream.
        This is achieved by reading chunk of bytes (of size chunk_size) at a
        time from the raw stream, and then yielding lines from there.
        """
        pending = b''
        for chunk in self.body.iter_chunks(chunk_size):
            lines = (pending + chunk).splitlines(True)
            for line in lines[:-1]:
                self.offset += len(line)
                yield line.decode('utf-8')
            pending = lines[-1]
        if pending:
            self.offset += len(pending)
            yield pending.decode('utf-8')
            
# def lambda_handler(event, context):
#     # TODO implement
#     handler(event, context)
#     return {
#         'statusCode': 200,
#         'body': json.dumps('Hello from Lambda!')
#     }
