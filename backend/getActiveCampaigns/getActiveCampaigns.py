from database import Campaign
import json
from datetime import datetime, timedelta


def get_active_campaigns(db):
    try:
        now = datetime.now() + timedelta(hours=8)
        campaigns = db.query(Campaign).filter(Campaign.start_date < now).filter(Campaign.end_date > now).all()
        result = []

        for campaignObj in campaigns:
            campaign = campaignObj.as_dict()
            campaign['end_date'] = str(campaign['end_date'])
            campaign['start_date'] = str(campaign['start_date'])
            campaign['rewards_program_id'] = str(campaign['rewards_program_id'])
            result.append(campaign)
            
        return result
        
    except Exception as err:
        db.rollback()
        raise err