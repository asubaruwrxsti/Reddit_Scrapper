from praw import Reddit
from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import time
from moviepy.editor import *
from pytube import YouTube
import random
import gtts

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

    path = f"./threads/{time.strftime('%-d%m%Y')}/{thread_id}"
    title_path = f"./threads/{time.strftime('%-d%m%Y')}/{thread_id}/title"
    comments_path = f"./threads/{time.strftime('%-d%m%Y')}/{thread_id}/comments"

    try:
        header = driver.find_element(By.XPATH, '//*[@id="SHORTCUT_FOCUSABLE_DIV"]/div[1]/header')
        driver.execute_script("arguments[0].removeAttribute('class')", header)

        reddit_title = driver.find_element(By.ID, f"t3_{thread_id}")
        driver.execute_script("arguments[0].scrollIntoView();", reddit_title)

        try:
            if not os.path.exists(path):
                os.makedirs(path)
                os.makedirs(title_path)
                os.makedirs(comments_path)
        except:
            print(f"Could not create folder for {thread_id} \n")

        reddit_title.screenshot(f'{title_path}/{thread_id}.png')
        print(f"Screenshot taken for title {thread_id} \n")

    except:
        print(f"Title {thread_id} not found, NSFW prompt\n")
        return

    for comment in comments[:comment_limit]:
        try:
            x_button = driver.find_element(By.CLASS_NAME, "_2qFn4QNDGodlEOt4HDqRcG")
            x_button.click()
            print("Closed 'Log In' prompt \n")

        except:
            print("No 'Log In' prompt")
        
        try:
            reddit_comment = driver.find_element(By.ID, f"t1_{comment.id}")
            reddit_comment.screenshot(f'{comments_path}/{comment.id}.png')

            #565, 130, 3
            if os.path.getsize(f"{comments_path}/{comment.id}.png") < 7000:
                os.remove(f".{comments_path}/{comment.id}.png")
            
            else:
                print(f"Screenshot taken for comment {comment.id} \n")    
                time.sleep(3)

        except:
            print(f"Comment {comment.id} not found \n")
            continue
    
    try:
        with open(f"{path}/{thread_id}.md", "w") as file:
            file.write(f"{thread_id} \n")
            file.write(f"{reddit_title.text} \n")
            for comment in comments[:comment_limit]:
                file.write(f"{comment.body} \n")
        
        comment_gtts_path = f"./threads/{time.strftime('%-d%m%Y')}/{thread_id}/comments_gtts/"
        if not os.path.exists(comment_gtts_path):
            os.makedirs(comment_gtts_path)
        
        for comment in comments[:comment_limit]:
            try:
                tts = gtts.gTTS(comment.body, lang='en')
                tts.save(f"{comment_gtts_path}/{comment.id}.mp3")
            except:
                print(f"Could not create .mp3 file for {comment.id} \n")
                continue
        
        try:
            title_gtts = gtts.gTTS(reddit_title.text, lang='en')
            title_gtts.save(f"{path}/title/title.mp3")
            print(f'Created .mp3 file for {thread_id} \n')
        except:
            print(f"Could not create .mp3 TITLE file for {thread_id} \n")
            return
        


    except:
        print(f"Could not create .md file for {thread_id} \n")
        return
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
    print("------------ Creating video ------------ \n")
    
    Download(link, base_clip_path= f"./threads/base_clip/")
    print("Base clip downloaded")

    if os.path.exists(f"./threads/{time.strftime('%-d%m%Y')}/{thread_id}"):
        output_path = f"./threads/{time.strftime('%-d%m%Y')}/{thread_id}/clip/"
        try:
            if not os.path.exists(output_path):
                os.makedirs(output_path)
        except:
            print(f"Could not create folder for {thread_id} \n")
            return
        
        
        clip = VideoFileClip(f"./threads/base_clip/base_video")
        print("Base clip loaded")
        print(f"Clip duration: {clip.duration} \n")

        number_of_comments = len(os.listdir(f"./threads/{time.strftime('%-d%m%Y')}/{thread_id}/comments"))
        comment_lengths = {}
        for comment in os.listdir(f"./threads/{time.strftime('%-d%m%Y')}/{thread_id}/comments_gtts"):
            comment_lengths[comment] = AudioFileClip(f"./threads/{time.strftime('%-d%m%Y')}/{thread_id}/comments_gtts/{comment}").duration


        clip_start = random.randint(20, int(clip.duration // 3))
        clip_end = (clip_start + 3) + [comment_lengths[comment] for comment in comment_lengths][0] 

        print(f"Clip start: {clip_start}")
        print(f"Clip end: {clip_end}")
        print(f"Number of comments: {number_of_comments} \n")

        clip = clip.subclip(clip_start, clip_end)
        print("Clip subclipped with length:", clip.duration/60, "minutes")

        title_clip = ImageClip(f"./threads/{time.strftime('%-d%m%Y')}/{thread_id}/title/{thread_id}.png")
        title_audio = AudioFileClip(f"./threads/{time.strftime('%-d%m%Y')}/{thread_id}/title/title.mp3")
        title_clip = title_clip.set_duration(title_audio.duration)
        title_clip = title_clip.set_start(0)
        print("Title clip created")

        clip = CompositeVideoClip([clip, title_clip.set_position(("center", "center"))])
        print("Title clip added to clip")

        clip_counter = title_clip.duration + 2
        for comment in os.listdir(f"./threads/{time.strftime('%-d%m%Y')}/{thread_id}/comments"):
            print(f"Adding comment {comment} to video")
            comment_clip = ImageClip(f"./threads/{time.strftime('%-d%m%Y')}/{thread_id}/comments/{comment}").set_duration(comment_lengths[comment[:-4]])
            comment_clip = comment_clip.set_start(clip_counter)
            comment_gtts_clip = AudioFileClip(f"./threads/{time.strftime('%-d%m%Y')}/{thread_id}/comments_gtts/{comment[:-4]}.mp3")
            clip = CompositeVideoClip([clip, comment_clip.set_position(("center", "center"))])
            clip = CompositeVideoClip([clip, comment_gtts_clip.set_start(clip_counter)])
            print(f"Comment {comment} added to video at {clip_counter} \n")

            clip_counter += comment_lengths[comment[:-4]] + 2

        try:
            print(f"\nProcessing video for {thread_id} \n")
            clip.write_videofile(f"{output_path}/{thread_id}.mp4", fps=24, codec="libx264", audio_codec="aac")
        except:
            print(f"Could not create video for {thread_id}")
            return
        
        print(f"Video created for {thread_id} \n")
    else:
        print(f'Could not find folder for {thread_id}, skipping \n')


if __name__ == "__main__":

    def getConfig():
        import configparser
        config = configparser.ConfigParser()
        config.read('config.ini')
        return config['CREDENTIALS']

    config = getConfig()

    username = config['username']
    client_id = config['client_id']
    secret = config['secret']
    password = config['password']
    user_agent = config['user_agent']
    subreddit_title = config['subreddit_title']
    subreddit_limit = int(config['subreddit_limit'])
    comment_limit = int(config['comment_limit'])

    print(f"Username: {username} \nPassword: {password} \nClient ID: {client_id} \nSecret: {secret} \nUser Agent: {user_agent} \n")

    window_size = {
        "width": 375,
        "height": 812
    }

    try:
        reddit = Reddit (
            client_id=client_id,
            client_secret=secret,
            username=username,
            password=password,
            user_agent=user_agent,
            read_only=True
        )
    except:
        print("Could not connect to Reddit \n")

    try:
        for submission in reddit.subreddit(subreddit_title).hot(limit=subreddit_limit):
            print(f'Submission title: {submission.title} - Submission ID: {submission.id}')
            create_image(submission.id, submission.comments, comment_limit, window_size)
            create_video(submission.id)
            print(f'Done !! {submission.id} \n')

    except Exception as e:
        print(e)
    
    print("------------ Done ------------ \n")
