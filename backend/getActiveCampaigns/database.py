""" Starts a session for the DB call """

# from pgsql.database import SessionLocal
from sqlalchemy import create_engine, ForeignKey, BIGINT, TypeDecorator, CHAR, Enum, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Boolean


import enum
import uuid

# connection
DATABASE_URL = "mysql+pymysql://admin:11111111@database-1.cluster-ro-cqbbxkouucyk.us-east-1.rds.amazonaws.com:3306/cs301_scis_bank"
# DATABASE_URL = "mysql+pymysql://admin:11111111@database-1-instance-1.cqbbxkouucyk.us-east-1.rds.amazonaws.com:3306/cs301_scis_bank"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



""" Starts a session for the DB call """
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


#####################################################################
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
    total_points = Column(Integer, nullable=False)
    total_miles = Column(Integer, nullable=False)
    total_cashback = Column(Integer, nullable=False)
    email = Column(String(255), nullable=False)
    usercard = relationship("UserCard", cascade="all, delete")


class UserCard(Base):
    """
    Our user table storing the users and their cards
    """
    __tablename__ = 'usercard'
    __table_args__ = {'extend_existing': True}
    card_pan_hash = Column(String(12), primary_key=True)
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
    rewards = Column(Integer)
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
    reward_type = Column(Enum(RewardType), nullable=False)


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
    
    def as_dict(self):
        return {c.name: getattr(self, str(c.name)) for c in self.__table__.columns}

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


class Code(Base):
    """
    OTP storage
    """
    __tablename__ = 'code'
    __table_args__ = {'extend_existing':True}
    codeID = Column(GUID, nullable=False, primary_key=True)
    userID = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)
