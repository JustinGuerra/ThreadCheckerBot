import praw
import operator
import time
import datetime
from praw.models import Comment

total_comments_processed = 0


def main():
    reddit = praw.Reddit("ThreadCheckBot")
    #subreddit = reddit.subreddit("news")
    #submissions = subreddit.hot(limit=10)
    # for submission in submissions:
    #check_thread(reddit, submission)

    check_thread(reddit, reddit.submission(id='a1y03b'))


def check_thread(reddit, submission):
    start_time = time.time()

    print("Checking Thread.")
    print("Thread Title: " + submission.title)
    print("Thread Id: " + submission.id)

    print("Grabbing all comments in thread...")
    all_comments_in_thread = get_all_comments(reddit, submission.id)
    print("Total Comments: " + str(len(all_comments_in_thread)))
    print("Getting all users in thread...")
    all_users_in_thread = get_all_unique_users(all_comments_in_thread)
    print("Total unique Users: " + str(len(all_users_in_thread)))

    top_subreddits = calculate_top_subreddits(all_users_in_thread)
    sorted_top_subreddits = sorted(
        top_subreddits.items(), key=operator.itemgetter(1))

    for result in sorted_top_subreddits:
        if result[0] != submission.subreddit and result[1] >= 15:
            print("Current thread has suspicious activity.")
            print("Thread has over 20 percent of users from a specific subreddit")
            print(result.display_name + ": " +
                  sorted_top_subreddits[result] + "%")
            print("Thread link: " + submission.permalink)

    runtime_in_seconds = int(round(time.time() - start_time))
    minutes, seconds = divmod(runtime_in_seconds, 60)
    hours, minutes = divmod(minutes, 60)

    print("Processed Thread in " + str(hours) + "h " +
          str(minutes) + "m " + str(seconds) + "s")


def calculate_top_subreddits(users):

    dict_of_primary_subreddits = {}

    print("Fetching top subreddits")
    user_counter = 0
    for user in users:
        if user:
            start_time = time.time()
            if type(user).__name__ == "Redditor":
                top_subreddit = fetch_subreddit_in_position(
                    user.comments.new(limit=None), 0)

                if top_subreddit in dict_of_primary_subreddits:
                    dict_of_primary_subreddits[top_subreddit] += 1
                else:
                    dict_of_primary_subreddits[top_subreddit] = 1
            user_counter += 1
            print("Processed user " + str(user_counter) +
                  " of " + str(len(users)))

    dict_of_subreddit_percentages = {}

    for subreddit in dict_of_primary_subreddits:
        percentage = (
            dict_of_primary_subreddits[subreddit] / len(users)) * 100

        dict_of_subreddit_percentages[subreddit] = percentage

    return dict_of_primary_subreddits


def fetch_subreddit_in_position(comments, position):
    subreddit_numbers = {}
    global total_comments_processed
    comments_processed_for_user = 0

    start_time = time.time()
    # Check each comment and grab the subreddit and increase tally for repeated subreddits
    for comment in comments:
        if comment:
            if type(comment).__name__ == "Comment":
                comment_date = datetime.datetime.utcfromtimestamp(
                    comment.created_utc)
                compare_date = datetime.datetime.now() - datetime.timedelta(days=365)
                if(comment_date >= compare_date):
                    if comment.subreddit in subreddit_numbers:
                        subreddit_numbers[comment.subreddit] += 1
                    else:
                        subreddit_numbers[comment.subreddit] = 1

                comments_processed_for_user += 1
                total_comments_processed += 1

    sorted_subreddits = sorted(
        subreddit_numbers.items(), key=operator.itemgetter(1))

    timeTook = time.time() - start_time
    print("Took " + str(timeTook) + " to process user")

    return sorted_subreddits[position][0]


def get_all_unique_users(comments):
    users = list()

    for comment in comments:
        if type(comment).__name__ == "Comment":
            if comment.author not in users:
                users.append(comment.author)

    return users


def get_sub_comments(comment, allComments):
    allComments.append(comment)
    if not hasattr(comment, "replies"):
        replies = comment.comments()
    else:
        replies = comment.replies
    for child in replies:
        get_sub_comments(child, allComments)


def get_all_comments(r, submissionId):
    submission = r.submission(submissionId)
    comments = submission.comments
    commentsList = []
    for comment in comments:
        get_sub_comments(comment, commentsList)
    return commentsList


if __name__ == "__main__":
    main()
