import json
from database import get_session
from getActiveCampaigns import get_active_campaigns

def lambda_handler(event, context):
    # TODO implement
    try:
        response = get_active_campaigns(db=get_session())
        return response
    except Exception as e:
        print(e)

    return False