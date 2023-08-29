import configparser
import pathlib
import sys
import psycopg2
from psycopg2 import sql
from validation import validate_input

"""
Part of DAG. Upload S3 CSV data to Redshift. Takes one argument of format YYYYMMDD. This is the name of 
the file to copy from S3. Script will load data into temporary table in Redshift, delete 
records with the same post ID from main table, then insert these from temp table (along with new data) 
to main table. This means that if we somehow pick up duplicate records in a new DAG run,
the record in Redshift will be updated to reflect any changes in that record, if any (e.g. higher score or more comments).
"""

# parser=configparser.ConfigParser()
# script_path = pathlib.Path(__file__).parent.resolve()
# config_file = "configuration.conf"
# parser.read(f"{script_path}/{config_file}")



REDSHIFT_USERNAME='REDSHIFT_USERNAME'
REDSHIFT_PASSWORD='REDSHIFT_PASSWORD'
REDSHIFT_ROLE='REDSHIFT_ROLE'
REDSHIFT_DATABASE='REDSHIFT_DATABASE'
REDSHIFT_PORT='REDSHIFT_PORT'
REDSHIFT_HOST='REDSHIFT_HOST'

ACCOUNT_ID='ACCOUNT_ID'

BUCKET_NAME='BUCKET_NAME'

TABLE_NAME = "reddit"

# Check command line argument passed
try:
    output_name = sys.argv[1]
except Exception as e:
    print(f"Command line argument not passed. Error {e}")
    sys.exit(1)

# Our S3 file & role_string
file_path = f"s3://{BUCKET_NAME}/{output_name}.csv"
role_string = f"arn:aws:iam::{ACCOUNT_ID}:role/{REDSHIFT_ROLE}"

# Create Redshift table if it doesn't exist
sql_create_table = sql.SQL(
    """CREATE TABLE IF NOT EXISTS {table} (
                            id varchar PRIMARY KEY,
                            title varchar(max),
                            author varchar(max),
                            score int,
                            upvote_ratio float,
                            num_comments int,
                            posting_time timestamp,
                            permalink varchar(max),
                            url varchar(max),
                            subreddit_id varchar(max)
                        );"""
).format(table=sql.Identifier(TABLE_NAME))


# If ID already exists in table, we remove it and add new ID record during load.
create_temp_table = sql.SQL(
    "CREATE TEMP TABLE our_staging_table (LIKE {table});"
).format(table=sql.Identifier(TABLE_NAME))
sql_copy_to_temp = f"COPY our_staging_table FROM '{file_path}' iam_role '{role_string}' IGNOREHEADER 1 DELIMITER ',' CSV;"
delete_from_table = sql.SQL(
    "DELETE FROM {table} USING our_staging_table WHERE {table}.id = our_staging_table.id;"
).format(table=sql.Identifier(TABLE_NAME))
insert_into_table = sql.SQL(
    "INSERT INTO {table} SELECT * FROM our_staging_table;"
).format(table=sql.Identifier(TABLE_NAME))
drop_temp_table = "DROP TABLE our_staging_table;"

def main():
    """Upload file form S3 to Redshift Table"""
    validate_input(output_name)
    rs_conn = connect_to_redshift()
    load_data_into_redshift(rs_conn)

def connect_to_redshift():
    """Connect to Redshift instance"""
    try:
        rs_conn = psycopg2.connect(
            dbname=REDSHIFT_DATABASE, user=REDSHIFT_USERNAME, password=REDSHIFT_PASSWORD, host=REDSHIFT_HOST, port=REDSHIFT_PORT
        )
        return rs_conn
    except Exception as e:
        print(f"Unable to connect to Redshift. Error {e}")
        sys.exit(1)


def load_data_into_redshift(rs_conn):
    """Load data from S3 into Redshift"""
    with rs_conn:

        cur = rs_conn.cursor()
        cur.execute(sql_create_table)
        cur.execute(create_temp_table)
        cur.execute(sql_copy_to_temp)
        cur.execute(delete_from_table)
        cur.execute(insert_into_table)
        cur.execute(drop_temp_table)

        rs_conn.commit()

if __name__ == "__main__":
    main()
