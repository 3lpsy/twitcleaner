# twitcleaner

This is a simple script that uses the python tweepy API to check accounts you are following and tell you which ones have been inactive for a certain amount of days.

**Note**
This requires twitter API account access. This is annoying to get because twitter doesn't like fun. You may have to wait multiple days to get your API approved. Before attempting to use this script, make sure you have API access.

### Setup

```
# requires python3's venv module
$ git clone https://github.com/3lpsy/twitcleaner
$ cd twitcleaner
$ python3 -m venv venv
$ source venv/bin/active
$ pip install -r requirements.txt
```

### Authentication

```
$ cp .env.example .env
# fill out the .env file with the correct values

# alternatively
export TWITTER_CONSUMER_KEY=theconsumerkeyvalue
export TWITTER_CONSUMER_SECRET=theconsumersecretvalue
export TWITTER_ACCESS_TOKEN=thesaccesstokenvalue
export TWITTER_ACCESS_SECRET=theaccesssecretvalue
```

## Getting Started

```
# you can omit -e .env if you used the export method
$ python3 twitclean.py -d 30 -u MyUserName -e .env

# alternatively, save list to file
$ python3 twitclean.py -d 30 -u MyUserName -e .env | tee ~/MyInactiveFollows.txt

# the default uses 30 days, you may want to lower this to 14 or something else depending on your needs
```

### Output

There are some debug messages printed out. You're likely to encounter rate limits at points. All messages, with the exception of the csv values `(username, user_id, last_created_at)`, are printed to stderr. An example output looks like:

```
[*] Loading environment file: .env
[*] Loading into environment: TWITTER_CONSUMER_KEY
[*] Loading into environment: TWITTER_CONSUMER_SECRET
[*] Loading into environment: TWITTER_ACCESS_TOKEN
[*] Loading into environment: TWITTER_ACCESS_SECRET
[*] Moving to next cohort
[*] Iteration halted on status for someuser1. Most likely the user is inactive.
[**] Failed test someuser1: 2021-05-16 08:01:12 < 2021-05-30 00:08:34.701867
[*] Iteration halted on status for someuser2. Most likely the user is inactive.
[**] Failed test someuser2: 2021-01-31 12:21:44 < 2021-05-30 00:08:34.701867
[*] Iteration halted on status for someuser3. Most likely the user is inactive.
[**] Failed test someuser3: 2021-04-30 14:13:22 < 2021-05-30 00:08:34.701867
someuser1,12345,2021-05-16 08:01:12
[*] Moving to next cohort
someuser2,23456,2021-01-31 12:21:44
someuser3,34567,2021-04-30 14:13:22
...
[!] Rate limit hit. Sleeping for a bit
```

Once the rate limit is hit, just wait. It'll take a bit. Everything is written to stderr except the CSV values so you'll definitely want to pipe it to a file. The date included in the CSV is the last identified tweet/activity. The 'Failed test' messages just mean that the person did not show activity with in the range specified. It's used for debugging and can be ignored.

### Improvements & Post Processing

I wrote this in about an hour. The output is pretty messy but it doesn't really matter **if piping stdout to a file**. This script does not do any automatic unfollowing. If you follow thousands or tens of thousands of accounts, this is probably not the script for you. It's expected you'll unfollow manually. Something like the following could work (untested):

```
# use open instead of xdg-open on mac. alternatively, call your browser CLI
$ for username in $(cat ~/MyInactiveFollows.txt | cut -d ',' -f1); do xdg-open https://twitter.com/${username}; done
```

The users are paginated. After each cohort, the inactive users will be printed out.

### Usage

```
usage: twitclean.py [-h] [-e ENV_FILE] [-d DAYS_PAST] [-P MAX_PAGES] -u
                    USERNAME

optional arguments:
  -h, --help            show this help message and exit
  -e ENV_FILE, --env-file ENV_FILE
                        A .env file containing API auth values
  -d DAYS_PAST, --days-past DAYS_PAST
                        List users who have not tweeted in past number of
                        days. (Default: 30)
  -P MAX_PAGES, --max-pages MAX_PAGES
                        Maximum number of pages to search. Mostly for testing
  -u USERNAME, --username USERNAME
                        Your username

```
