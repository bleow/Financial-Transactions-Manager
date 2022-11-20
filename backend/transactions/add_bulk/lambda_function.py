import numpy as np
from pymysql import NULL

from backend.database_seeder import seed_db
from backend.transactions.add_bulk.database import get_session
from backend.transactions.add_bulk.process_transaction import process_transaction


def lambda_handler():
    db = get_session()
    # seed_db(db)

    import boto3
    import pandas as pd
    from io import StringIO

    client = boto3.client('s3')
    bucket_name = 'batchuploadbucket'
    object_key = 'public/Project B (Appendix 2a) - spend.first.1000.csv'
    csv_obj = client.get_object(Bucket=bucket_name, Key=object_key)
    body = csv_obj['Body']
    csv_string = body.read().decode('utf-8')
    df = pd.read_csv(StringIO(csv_string))
    df = df.replace(np.nan, NULL)

    failed_transactions = []
    for row_dict in df.to_dict(orient="records"):
        process_transaction(db, row_dict, failed_transactions)

    return failed_transactions


if __name__ == "__main__":
    print('end bulk add', lambda_handler())
