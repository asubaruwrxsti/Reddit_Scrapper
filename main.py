from praw import Reddit
from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import time
from moviepy.editor import *
from pytube import YouTube

def create_image(thread_id, comments, comment_limit = 1, window_size = {"width": 375, "height": 812}):
    url = f"https://www.reddit.com/r/AskReddit/comments/{thread_id}"
    
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--incognito")
    options.add_argument(f"--window-size={window_size['width']},{window_size['height']}")

    driver = webdriver.Chrome(options=options)

    driver.get(url)
    driver.execute_script()

    path = f"./threads/{time.strftime('%-d%m%Y')}/{thread_id}"
    title_path = f"./threads/{time.strftime('%-d%m%Y')}/{thread_id}/title"
    comments_path = f"./threads/{time.strftime('%-d%m%Y')}/{thread_id}/comments"

    try:

        # add hidden attribute to header of reddit
        header = driver.find_element(By.XPATH, '//*[@id="SHORTCUT_FOCUSABLE_DIV"]/div[1]/header')
        driver.execute_script("arguments[0].removeAttribute('class')", header)

        reddit_title = driver.find_element(By.ID, f"t3_{thread_id}")

        try:
            if not os.path.exists(path):
                os.makedirs(path)
                os.makedirs(title_path)
                os.makedirs(comments_path)
        except:
            print(f"Could not create folder for {thread_id} \n")
        
        # scroll to comment
        driver.execute_script("arguments[0].scrollIntoView();", reddit_title)
        reddit_title.screenshot(f'{title_path}/{thread_id}.png')
        print(f"Screenshot taken for title {thread_id} \n")
    except:
        print(f"Title {thread_id} not found, +18 or NSFW prompt\n")
        return

    for comment in comments[:comment_limit]:
        try:
            # hide LOGIN if present
            x_button = driver.find_element(By.CLASS_NAME, "_2qFn4QNDGodlEOt4HDqRcG")
            x_button.click()
            print("Closed 'Log In' prompt \n")

        except:
            print("No 'Log In' prompt \n")
        
        #if element is not found skip
        try:
            reddit_comment = driver.find_element(By.ID, f"t1_{comment.id}")

            reddit_comment.screenshot(f'{comments_path}/{comment.id}.png')

            #565, 130, 3
            if os.path.getsize(f"{comments_path}/{comment.id}.png") < 7000:
                os.remove(f".{comments_path}/{comment.id}.png")
            
            time.sleep(3)

        except:
            print(f"Comment {comment.id} not found \n")
            continue
    print("------------ Done ------------ \n")
    driver.quit()


def Download(link, base_clip_path):
    youtubeObject = YouTube(link)
    youtubeObject = youtubeObject.streams.get_highest_resolution()
    try:
        if not os.path.exists(base_clip_path):
            os.makedirs(base_clip_path)

            youtubeObject.download(output_path= base_clip_path, filename="base_video")
            print("Download is completed successfully")
        else:
            print("File already exists")
    except:
        print("An error has occurred")

def create_video(thread_id, link = "https://www.youtube.com/watch?v=n_Dv4JMiwK8"):
    
    Download(link, base_clip_path= f"./threads/base_clip/")

    output_path = f"./threads/{time.strftime('%-d%m%Y')}/{thread_id}/clip/"
    
    try:
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        print("Folder created")

        

    except:
        print(f"Could not create folder for {thread_id} \n")
        return

def getConfig():
    import configparser
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['CREDENTIALS']

config = getConfig()

username = config['username']
password = config['password']
client_id = config['client_id']
secret = config['secret']
user_agent = config['user_agent']


subreddit_title = "askreddit"
subreddit_limit = 5
comment_limit = 10

window_size = {
    "width": 375,
    "height": 812
}

reddit = Reddit (
    client_id=client_id,
    client_secret=secret,
    username=username,
    password=password,
    user_agent=user_agent
    )

for submission in reddit.subreddit(subreddit_title).hot(limit=subreddit_limit):
    print(f'Submission title: {submission.title} - Submission ID: {submission.id}')
    create_image(submission.id, submission.comments, comment_limit, window_size)
