import datetime
import re
import string


def clean_raw_text(text):
    """
    Clean raw post/comment text with standard preprocessing pipeline
    """
    # Lowercasing text
    text = text.lower()
    # Removing not printable characters
    text = "".join(filter(lambda x: x in string.printable, text))
    # Removing XSLT tags
    text = re.sub(r"&lt;/?[a-z]+&gt;", "", text)
    text = text.replace(r"&amp;", "and")
    text = text.replace(r"&gt;", "")
    # Removing newline, tabs and special reddit words
    text = text.replace("\n", " ")
    text = text.replace("\t", " ")
    text = text.replace("[deleted]", "").replace("[removed]", "")
    # Removing URLs
    text = re.sub(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        "",
        text,
    )
    # Removing numbers
    text = re.sub(r"\w*\d+\w*", "", text)
    # Removing Punctuation
    text = text.translate(str.maketrans("", "", string.punctuation))
    # Removing extra spaces
    text = re.sub(r"\s{2,}", " ", text)
    # Stop words? Emoji?
    return text


def process_post(raw_post, is_post=True):
    post_attributes = {
        "id": None,
        "author": None,
        "created_utc": None,
        "num_comments": None,
        "over_18": None,
        "is_self": None,
        "score": None,
        "selftext": None,
        "stickied": None,
        "subreddit": None,
        "subreddit_id": None,
        "title": None,
    }

    user_id = raw_post["author"]
    post = dict()  # dict to store posts
    # adding field category
    # adding field date in a readable format
    post["date"] = datetime.datetime.utcfromtimestamp(
        int(raw_post["created_utc"])
    ).strftime("%d/%m/%Y")
    # cleaning body field

    if is_post:
        merged_text = raw_post["title"] + " " + raw_post["selftext"]
        post["clean_text"] = clean_raw_text(merged_text)
    else:
        post["clean_text"] = clean_raw_text(raw_post["body"])
        post["link_id"] = raw_post["link_id"]
        post["parent_id"] = raw_post["parent_id"]

    # selecting fields
    for attr in post_attributes:
        if attr not in raw_post:  # handling missing values
            post[attr] = None
        elif (attr != "selftext") and (attr != "title"):  # saving only clean text
            post[attr] = raw_post[attr]

    return user_id, post, int(raw_post["created_utc"])
