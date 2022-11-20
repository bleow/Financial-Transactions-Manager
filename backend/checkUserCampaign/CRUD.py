from sqlalchemy import *
from database import RewardsProgram
from sqlalchemy.orm.session import Session


        
# get base programs by card with exclusions
def getCardProgramsByCardID(db: Session, card_type):
    try:
        cardPrograms = db.query(RewardsProgram).filter(RewardsProgram.card_type == card_type).filter(or_(RewardsProgram.earn_type == "BER", RewardsProgram.earn_type == "AC")).all()
        cardProgList = [cardProgram.as_dict() for cardProgram in cardPrograms]
        return 200, cardProgList
        
    except Exception as err:
        return 400, err
        
        
from sqlalchemy import *
from database import RewardsProgram, Campaign
from sqlalchemy.orm.session import Session
from datetime import datetime

        
# get campaigns by card with campaign date
def getCampaigns(db: Session, cardID):
    try:
        now = datetime.now()
        print(cardID)
        campaigns = db.query(Campaign, RewardsProgram).outerjoin(RewardsProgram, Campaign.rewards_program_id == RewardsProgram.rewards_program_id).filter(and_((Campaign.start_date < now),(Campaign.end_date > now), (RewardsProgram.card_type==cardID))).all()
        campaignList = []
        print(cardID)
        for obj in campaigns:
            obj1 = obj[0].as_dict()
            obj2 = obj[1].as_dict()
            for property in obj2:
                obj1[property] = obj2[property]

            campaignList.append(obj1)
            
        return 200, campaignList
    except Exception as err:
        return 400, err
        
        
from database import Exclusions

def getExclusions(db, reward_type):
    try:
        exclusions = db.query(Exclusions.mcc).filter(Exclusions.reward_type==reward_type).all()
        return exclusions
    except Exception as e:
        return e

from sqlalchemy import *
from database import UnprocessedTransactions as Transaction
from sqlalchemy.orm.session import Session


def getTransByCard(db: Session, cardID):
    try:
        transactions = db.query(Transaction).filter(Transaction.card_type == cardID).all()
        transactionList = [transaction.as_dict() for transaction in transactions]

        return 200, transactionList
        
    except Exception as err:
        return 400, err

def get1000TransByCard(db: Session, cardID):
    try:
        transactions = db.query(Transaction).filter(Transaction.card_type == cardID).limit(50).all()
        transactionList = [transaction.as_dict() for transaction in transactions]

        return 200, transactionList
        
    except Exception as err:
        return 400, err

from sqlalchemy import update
from database import ProcessedTransactions, UnprocessedTransactions
 
def update_transaction(db, points,reward_type, transaction):
    try:
        print(1)
        processed_transaction_dict = {
            "transaction_id": transaction['transaction_id'],
            "merchant": transaction['merchant'],
            "amount": transaction['amount'],
           "transaction_date": transaction['transaction_date'],
            "card_type" : transaction['card_type'],
            "rewards" : points,
            "user_id": transaction['user_id'],
            "reward_type" : reward_type
        }
        trans = ProcessedTransactions(**processed_transaction_dict)
        print(2)
        db.add(trans)
        to_remove = db.query(UnprocessedTransactions).filter(transaction['transaction_id'] == UnprocessedTransactions.transaction_id).first()
        db.delete(to_remove)
        db.commit()
        print(3)
        return True
    except Exception as err:
        raise err
        return "could not update processed transaction"
        
from sqlalchemy import update
from database import User
 
def update_user(db, points, reward_type, user_id):
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        col = 'total_'+reward_type.lower()
        setattr(user, col, getattr(user,col)+points)
        db.commit()
        return True
        
    except Exception as err:
        raise err
        return False
        
        
# def update_user(db, points, reward_type, user_id):
#     try:
#         user = db.query(User).filter(User.User_ID == user_id).first()
        
#         if reward_type=="Points":
#             user.Points_Total += points
#         elif reward_type=="Cashback":
#             user.Cashback_Total += points
#         elif reward_type=="Miles":
#             user.Miles_Total += points

#         db.commit()
#         return True
        
#     except Exception as err:
#         raise err
#         return False
