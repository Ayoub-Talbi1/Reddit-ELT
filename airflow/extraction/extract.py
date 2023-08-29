import configparser
import datetime
import pathlib
import sys
import praw
import pandas as pd
import sys
from validation import validate_input


"""
Part of Airflow DAG. Takes in one command line argument of format YYYYMMDD. 
Script will connect to Reddit API and extract top posts from past day
with no limit. For a small subreddit like Data Engineering, this should extract all posts
from the past 24 hours.
"""


# parser = configparser.ConfigParser()
# script_path = pathlib.Path(__file__).parent.resolve()
# config_file = "configuration.conf"
# parser.read(f"{script_path}/{config_file}")
SECRET = 'Reddit-SECRET'
CLIENT_ID = 'CLIENT-ID'
USER_AGENT = 'reddit_ELT_app'

SUBREDDIT = 'dataengineering'
TIME_FILTER = 'day'
LIMIT = None


# Use command line argument as output file
# name and also store as column value
try:
    output_name = sys.argv[1]
except Exception as e:
    print(f"Error with file input. Error {e}")
    sys.exit(1)
date_dag_run = datetime.datetime.strptime(output_name, "%Y%m%d")


def main():
    validate_input(output_name)
    reddit=connect_api(SECRET,CLIENT_ID,USER_AGENT)
    data=extract_data(reddit)
    load_to_csv(data)


def connect_api(secret,client_id,user_agent):
    try:
        instance=praw.Reddit(client_id=client_id,client_secret=secret,user_agent=user_agent)
        return instance
    except Exception as e:
        print(f"Error with file input. Error {e}")
        sys.exit(1)


def extract_data(reddit_instance):
    subreddit = reddit_instance.subreddit(SUBREDDIT)
    posts = subreddit.top(time_filter=TIME_FILTER, limit=LIMIT)
    ids = []
    titles = []
    authors = []
    scores = []
    upvote_ratio = []
    number_of_comments = []
    posting_times = []
    permalinks = []
    urls = []
    subreddit_id = []
    for post in posts:
        try:
            ids.append(post.id)
            titles.append(post.title)
            authors.append(post.author)
            scores.append(post.score)
            upvote_ratio.append(post.upvote_ratio)
            number_of_comments.append(post.num_comments)
            posting_times.append(post.created_utc)
            permalinks.append(post.permalink)
            urls.append(post.url)
            subreddit_id.append(post.subreddit_id)
        except Exception as e:
            print(f"there has been an issue, Error: {e}")
    data = {'id': ids, 'title': titles, 'author': authors, 'score': scores, 'upvote_ratio': upvote_ratio, 'number_of_comments': number_of_comments,
        'time': posting_times, 'permalink': permalinks, 'url': urls, 'subreddit_id': subreddit_id}

    df = pd.DataFrame(data)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    return df


def load_to_csv(extracted_data_df):
    """Save extracted data to CSV file in /tmp folder"""
    extracted_data_df.to_csv(f"/tmp/{output_name}.csv", index=False)


if __name__ == '__main__':
    main()
