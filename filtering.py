import requests
import json
import bz2
import lzma
import os
from text_utils import *
import datetime
import zstandard
import io
import tqdm
import pathlib
from collections import defaultdict



def read_file(filename):
    filetype = filename.rsplit(".")[-1]

    if filetype == "bz2":
        comm_file = bz2.BZ2File(f"{filename}")
        while True:

            line = comm_file.readline()
            if len(line) == 0:
                break
            try:
                post = json.loads(line)
                yield post
            except:
                pass

    elif filetype == "xz":
        comm_file = lzma.open(f"{filename}")
        while True:

            line = comm_file.readline()
            if len(line) == 0:
                break
            try:
                post = json.loads(line)
                yield post
            except:
                pass

    elif filetype == "zst":
        with open(f"{filename}", "rb") as fh:
            dctx = zstandard.ZstdDecompressor(max_window_size=2147483648)
            stream_reader = dctx.stream_reader(fh)
            text_stream = io.TextIOWrapper(stream_reader, encoding="utf-8")
            for line in text_stream:
                try:
                    post = json.loads(line)
                    yield post
                except:
                    pass
    else:
        print("ERRORE: tipo file non valido")


def comment_filter(filename, subreddits):
    users = {}


    print("Parsing...")
    for comment in tqdm.tqdm(read_file(filename)):
        try:
            if "subreddit" in comment:
                subr = comment["subreddit"]
                if subr in subreddits:
                    if comment["author"] in ["[deleted]", "AutoModerator"]:
                        continue

                    if comment["body"] != "[deleted]":
                        user, pdescr, current_date_post = process_post(
                            raw_post=comment, is_post=False
                        )

                        pdescr["date"] = pdescr["date"][3:] # by month
                        if user in users:

                            if pdescr["date"] in users[user]["comments"]:
                                users[user]["comments"][pdescr["date"]].append(pdescr)
                            else:
                                users[user]["comments"][pdescr["date"]] = [pdescr]
                        else:
                            users[user] = {
                                "posts": {},
                                "comments": {pdescr["date"]: [pdescr]},
                            }

        except Exception:
            pass

    write_users(users)


def submission_filter(filename, subreddits):
    users = {}

    print("Parsing...")
    for post in tqdm.tqdm(read_file(filename)):
        try:
            if "subreddit" in post:
                subr = post["subreddit"]

                if subr in subreddits:

                    if post["author"] in ["[deleted]", "AutoModerator"]:
                        continue
                    user, pdescr, current_date_post = process_post(post, is_post=True)
                    pdescr["date"] = pdescr["date"][3:] # by month

                    if user in users:


                        if pdescr["date"] in users[user]["posts"]:
                            users[user]["posts"][pdescr["date"]].append(pdescr)
                        else:
                            users[user]["posts"][pdescr["date"]] = [pdescr]
                    else:
                        users[user] = {"posts": {pdescr["date"]: [pdescr]}, "comments": {}}

        except Exception:
            pass

    write_users(users)


def write_users(users):
    print("writing...")

    for ti, tp in enumerate([users]):
        for user, u_data in tqdm.tqdm(tp.items()):
            try:
                if os.path.exists(f"raw_data/{user}.json"):
                    old_data = json.load(open(f"raw_data/{user}.json"))
                    for k, v in old_data["comments"].items():
                        u_data["comments"][k] = v
                    for k, v in old_data["posts"].items():
                        u_data["posts"][k] = v

                with open(f"raw_data/{user}.json", "w") as outfile:
                    jsonData = json.dumps(u_data, indent=1)
                    outfile.write(jsonData)
            except:
                pass



if __name__ == "__main__":

    # Path to the dump folder
    base_path = r"C:\Users\Alessandro Batignani\Desktop\SNA"

    # submission zst files are expected under base_path/submission,
    # comments under base_path/comments

    # subreddits of interest
    subreddits = json.load(open("subreddits.json"))

    # dump files
    comments = json.load(open("comments_idx.json"))
    submissions = json.load(open("submissions_idx.json"))

    # output
    pathlib.Path("raw_data_february/").mkdir(parents=True, exist_ok=True)

    with open("log.txt", "w") as log:

        print("Processing submissions...")
        for submission_f in tqdm.tqdm(submissions):
            submission_f = f"{base_path}/submissions/{submission_f}"
            submission_filter(
                submission_f,
                subreddits
            )
            log.write(f"{submission_f} complete\n")

        print("Processing comments...")
        for comment_f in tqdm.tqdm(comments):
            comment_f = f"{base_path}/comments/{comment_f}"
            comment_filter(
                comment_f,
                subreddits,
            )
            log.write(f"{comment_f} complete\n")
