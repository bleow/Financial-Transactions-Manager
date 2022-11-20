from database import get_session
from getBaseProgramsByCard import getCardProgramsByCardID
# getCardPrograms
from getCampaignsByCard import getCampaigns
from getTransactionByCard import getTransByCard, get1000TransByCard
from updateUser import update_user
from updateTransaction import update_transaction
from getExclusions import getExclusions
import json
import boto3

client = boto3.client('lambda')
MINIMUN_REMAINING_TIME_MS = 5000

# def lambda_handler(event, context):
#     try:
#         cardID = json.loads(event["Records"][0]["body"])["cardID"]
#         db_session = get_session()
#         code, response = getCardPrograms(db=get_session()) # get base card programs by 
#         # {k: v for k, v in sorted(x.items(), key=lambda item: item[1])} -> need to sort or smtg
#         print(code)
#         print(response)
#         for card_id in response.keys(): # looping through cards to get transactions
#             transactions = getTransByCard(db=db_session, cardID = card_id)
#             cal_campaign(db_session, transactions)
#             baseList = response[card_id]
#             cal_base(db_session, baseList, transactions)
#         return True
            
    
#     except Exception as e:
#         print(e)

#     return False

#edited to handle cardID event
def lambda_handler(event, context):
    try:
        cardID = json.loads(event["Records"][0]["body"])["cardID"]
        db_session = get_session()
        code, response = getCardProgramsByCardID(db=get_session(), card_type = cardID) # get base card programs by 
        print(response)
        # {k: v for k, v in sorted(x.items(), key=lambda item: item[1])} -> need to sort or smtg
        # print(1)
        # transactions = getTransByCard(db=db_session, cardID = cardID)
        transactions = get1000TransByCard(db=db_session, cardID = cardID)
        print("meepppp")
        print(transactions[1])
        while len(transactions[1]) > 0:
            # print(2)
            cal_campaign(db_session, transactions[1])
            # print(3)
            baseList = response
            cal_base(db_session, baseList, transactions[1])
            transactions = get1000TransByCard(db=db_session, cardID = cardID)
            print(transactions[1])

            if context.get_remaining_time_in_millis() < MINIMUN_REMAINING_TIME_MS and len(transactions[1]) > 0:
                print('no more time', context.get_remaining_time_in_millis())
                invoke_lambda('checkUserCampaign',event)
                break
        return 'function ended'
    except Exception as e:
        print(e)


def cal_base(db_session, baseList, transactions):
    for transaction in transactions:
        print(transaction)
        # rewardsInfo = []
        # #check for stackable
        # print(baseList[0])
        # card_type = str(baseList[0]["card_type"].name)
        # print("This is my card:" + card_type)
         
        # for program in baseList:
        #     print(baseList)
        #     status, amount, earn_type = check_applicable(program, transaction)
        #     if status:
        #         if baseList[0]['is_stackable'] == True:
        #             if rewardsInfo ==[]:
        #                 rewardsInfo.append([amount, earn_type])
        #             else:
        #                 for reward in range(len(rewardsInfo)):
        #                     if (earn_type == rewardsInfo[reward][1]) and (amount > rewardsInfo[reward][0]):
        #                         rewardsInfo[reward][0]=amount
        #         else: 
        #             if rewardsInfo == []:
        #                 rewardsInfo.append(amount)
        #             else:
        #                 if amount > rewardsInfo[0]:
        #                     rewardsInfo=[amount]

        # if len(rewardsInfo) == 1:
        #     points=rewardsInfo[0]
        # else:
        #     points=0 
        #     for rewards in rewardsInfo:
        #         points+=rewards[0]
        # print(4)
        # transStatus = update_transaction(db=db_session, points=round(points*transaction['amount'],2),reward_type=, transaction=transaction)
        # print(5)
        # userStatus = update_user(db=db_session, points=round(points*transaction['amount'],2), reward_type=str(baseList[0]["reward_type"].name), user_id=transaction["user_id"])
        # print(6)
        
        rewardInfo = {}
        card_type =  str(baseList[0]["card_type"].name)

        for program in baseList:
            status, amount, earn_type = check_applicable(program, transaction)
            print(status, amount, earn_type)
            if status:
                if earn_type not in rewardInfo:
                    rewardInfo[earn_type] = amount
                    print('new')
                elif baseList[0]['is_stackable'] == True:
                    rewardInfo[earn_type] += amount
                    print('stack')
                elif rewardInfo[earn_type] < amount:
                    rewardInfo[earn_type] = amount
                    print("max")
            elif not status:
                print("in here")
                continue
        # print(rewardInfo[earn_type])
        if rewardInfo:
            print(4, rewardInfo[earn_type])
            transStatus = update_transaction(db=db_session, points=round(rewardInfo[earn_type]*transaction['amount'],2),reward_type=earn_type, transaction=transaction)
            print(5)
            userStatus = update_user(db=db_session, points=round(rewardInfo[earn_type]*transaction['amount'],2), reward_type=str(baseList[0]["reward_type"].name), user_id=transaction["user_id"])
            print(6)
        else:
            transStatus = update_transaction(db=db_session, points=0,reward_type=earn_type, transaction=transaction)
            print(55)
            userStatus = update_user(db=db_session, points=0, reward_type=str(baseList[0]["reward_type"].name), user_id=transaction["user_id"])
            print(66)

    
def check_applicable(program, transaction):
    print(1000)
    print(program)
    try:
        exclusions = getExclusions(db=get_session(), reward_type=program['reward_type'].name)
    except Exception as err:
        print(err)
        exclusions=[]
    print(1001)
    print(exclusions)
    print(transaction)
    if (transaction['mcc'] not in exclusions) and (transaction["amount"] > program["min_spend"]) and (transaction['decorator_id'] == program['decorator_id']):
        print(1002)
        return True, program['amount'], program['earn_type'].name
    print(1003)
    return False, 0, "not applicable"
    
    
    
def cal_campaign(db_session, transactions): #get amount spent and merchant to see if it applies 

    try: 
        campaigns = getCampaigns(db_session, transactions[0]["card_type"])
    
        
    except Exception as e:
        return e, "No campaigns"
        
    for transaction in transactions: #loop through all transactions and if more than one campaign is applicable it is stackable 
        for campaign in campaigns[1]:
            # check campaign conditions
            if (transaction["amount"] > campaign["min_spend"]) \
            and (transaction["merchant"] == campaign["merchant"]) \
            and (transaction["transaction_date"] < campaign["end_date"])\
            and (transaction["transaction_date"] > campaign["start_date"]):
                
                #calculate rewards
                points = round(transaction["amount"] * campaign["amount"], 2)
                #update rewards
                transStatus = update_transaction(db=db_session, points= points, reward_type=campaign["reward_type"], transaction=transaction)
                userStatus = update_user(db=db_session, points=points, reward_type=campaign["reward_type"], user_id=transaction["user_id"])
    return "done"
                
                
def invoke_lambda(function_name, event):
    payload = json.dumps(event).encode('utf-8')
    response = client.invoke(
        FunctionName=function_name,
        InvocationType='Event',
        Payload=payload
    )