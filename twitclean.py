#!/usr/bin/env python3
from typing import Iterator, List, Tuple, Union
from os import environ
import sys
from signal import signal, SIGINT
from pathlib import Path
from datetime import datetime, timedelta
from tweepy import OAuthHandler, API, User, RateLimitError, Cursor, Status
import argparse
import time

def eprint(*args, **kwargs):
    print(*args,file=sys.stderr, **kwargs)

def sigint(received, frame):
    eprint("SIGINT or CTRL-C received. Giving up.")
    sys.exit(0)

def getenv(key):
    val = environ.get(key, None)
    if val is None or not val:
        eprint(f"[!] Please set environment variable in dotenv file or environment: {key}")
        sys.exit(1)
    return val

def loadenv(env_file):
    env_file = env_file or ".env"
    if Path(env_file).is_file():
        eprint(f"[*] Loading environment file: {env_file}")
        text_ = Path(".env").read_text()
        lines = text_.split("\n")
        for line in lines:
            if not line.startswith("#"):
                line = line.strip()
                pair = line.split("=", 1)
                if len(pair) == 2:
                    k = pair[0]
                    val = pair[1].strip("\"")
                    eprint(f"[*] Loading into environment: {k}")
                    environ[k] = val

def make_api():
    CONSUMER_KEY = getenv("TWITTER_CONSUMER_KEY")
    CONSUMER_SECRET = getenv("TWITTER_CONSUMER_SECRET")
    ACCESS_TOKEN = getenv("TWITTER_ACCESS_TOKEN")
    ACCESS_SECRET = getenv("TWITTER_ACCESS_SECRET")
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    return API(auth)

def user_limit(cursor)-> Iterator[List[User]]:
    while True:
        try:
            yield cursor.next()
        except RateLimitError:
            eprint("[!] Rate limit hit. Sleeping for a bit")
            time.sleep(15 * 60) 
        except StopIteration:
            eprint("[*] Iteration halted for user listing. Most likely the page limit has been hit")
            break

def status_limit(cursor, username)-> Iterator[Status]:
    while True:
        try:
            yield cursor.next()
        except RateLimitError:
            eprint("[!] Rate limit hit. Sleeping for a bit")
            time.sleep(15 * 60) 
        except StopIteration:
            eprint(f"[*] Iteration halted on status for {username}. I did not plan for this.")
            break

def run(username, days_past, env_file=None, max_pages=None):
    if env_file:
        loadenv(env_file)
    api = make_api()
    _max_pages = max_pages or -1
    date_cutoff = datetime.now() - timedelta(days=days_past)
    inactive_users: List[Tuple[str, str, Union[datetime, None]]] = []
    for page in user_limit(Cursor(api.friends, username).pages(_max_pages)):
        inactive_cohort: List[Tuple[str, str, Union[datetime, None]]] = []
        for user in page:
            is_active_user = False
            # typing messed up
            udata = user._json
            user_id: str =  udata["id"]
            user_username: str = udata["screen_name"]
            newest_created_at = None
            #print(f"[*] Reviewing user {user_username} - {user_id}")
            # alternatively just use the model
            scursor = Cursor(api.user_timeline, user_id=user_id).items(3)
            for tweet in status_limit(scursor, user_username):
                # typing messed up
                created_at: datetime = tweet.created_at
                if not newest_created_at:
                    newest_created_at = created_at
                if created_at >= date_cutoff:
                    #print(f"[**] Passes test: {str(created_at)}")
                    is_active_user = True
                    break
            if not is_active_user:
                eprint(f"[**] Failed test: {str(newest_created_at)} < {date_cutoff}")
                u = (user_username, user_id, newest_created_at)
                inactive_cohort.append(u)
        # at end of each page, print out users
        for u in inactive_cohort:
            user_username = u[0]
            user_id = u[1]
            newest_created_at = u[2]
            print(f"{user_username},{user_id},{newest_created_at}")
            inactive_users.append(u)
        eprint("[*] Moving to next cohort")
        time.sleep(5)
    eprint("[*] Listing complete")

if __name__ == "__main__":
    signal(SIGINT, sigint)
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--env-file", type=str, help="A .env file containing API auth values")
    parser.add_argument("-d", "--days-past", type=int, default=30, help="List users who have not tweeted in past number of days. (Default: 30)")
    parser.add_argument("-P", "--max-pages", type=int, help="Maximum number of pages to search. Mostly for testing")
    parser.add_argument("-u", "--username", type=str, required=True, help="Your username")
    args = parser.parse_args()
    run(args.username, args.days_past, args.env_file, args.max_pages)


