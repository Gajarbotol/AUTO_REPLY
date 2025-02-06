import requests
import time
import os
from flask import Flask

# Flask অ্যাপ তৈরি করুন
app = Flask(__name__)

# লগইন তথ্য
login_url = 'https://golperjhuri.com/login.php'
story_url = 'https://golperjhuri.com/story.php?id=41225'

login_data = {
    'user_email': 'autoreply@gmail.com',
    'user_pass': '####11Aa',
    'remamber': 'on'
}

# সেশন তৈরি করুন
session = requests.Session()

# লগইন করুন
login_response = session.post(login_url, data=login_data)

if "AUTO REPLY" not in session.get('https://golperjhuri.com/dashboard/dashboard.php').text:
    print("Login failed or 'AUTO REPLY' not found")
    exit()

print("Successfully logged in - AUTO REPLY")

# বটের অবস্থা (ডিফল্ট: বন্ধ)
bot_active = False

# Keep-alive ফাংশন (Render সার্ভার বন্ধ হওয়া ঠেকাতে)
def keep_alive():
    while True:
        try:
            requests.get("https://auto-reply-i49c.onrender.com/ping")
            print("Pinged to keep alive.")
        except Exception as e:
            print("Ping failed:", e)
        time.sleep(900)  # প্রতি ১৫ মিনিটে পিং করবে

# Ping রুট (Render সার্ভারকে সক্রিয় রাখতে)
@app.route("/ping")
def ping():
    return "Pong!", 200

# মূল বট লুপ
def bot_loop():
    global bot_active
    while True:
        print("Checking for commands...")

        # স্টোরি পেজ লোড করুন
        story_response = session.get(story_url)
        soup = BeautifulSoup(story_response.text, 'html.parser')

        # সব কমেন্ট বের করুন
        comments = soup.find_all("div", class_="comment-main-level")

        for comment in comments:
            user_name_tag = comment.find("h6", class_="comment-name")
            comment_content_tag = comment.find("div", id=lambda x: x and "comment-content" in x)

            if user_name_tag and user_name_tag.a and comment_content_tag:
                username = user_name_tag.a.text.strip()
                comment_text = comment_content_tag.text.strip()

                # TURN ON / TURN OFF চেক করুন
                if username == "丂卄ㄖ卄卂几":
                    if "TURN ON" in comment_text and not bot_active:
                        bot_active = True
                        confirmation_reply = "Turned on successfully!"
                    elif "TURN OFF" in comment_text and bot_active:
                        bot_active = False
                        confirmation_reply = "Turned off successfully!"
                    else:
                        confirmation_reply = None

                    # নিশ্চিতকরণ বার্তা পাঠানো
                    if confirmation_reply:
                        reply_text = f"{confirmation_reply}\n@{username}"
                        comment_data = {
                            "c_name": "AUTO REPLY",
                            "c_story": "41225",
                            "c_comment": reply_text,
                            "comment_submit": "মন্তব্য করুন"
                        }
                        post_response = session.post(story_url, data=comment_data)

                        if post_response.status_code == 200:
                            print(f"Command reply posted: {confirmation_reply}")
                        else:
                            print("Failed to post command reply!")

                # যদি বট চালু থাকে তাহলে @AUTO REPLY মেনশন খুঁজবে
                if bot_active and "@AUTO REPLY" in comment_text:
                    print(f"@AUTO REPLY mentioned by {username}: {comment_text}")

                    # API থেকে উত্তর নিয়ে আসা
                    api_url = f"https://api.reshu.whf.bz/chat.php?id=00&q=Answer+this+using+bangla+and+try+to+make+answer+too+short+and+emoji+codes+:)+:)+:D+:huh:+:Icecream:+:yucky:+:angary:+:lovely:+and+you+have+answer+to+this+question+{comment_text}"
                    api_response = requests.get(api_url)

                    if api_response.status_code == 200:
                        reply_text = f"{api_response.text.strip()}\n@{username}"
                        print(f"Replying: {reply_text}")

                        # কমেন্ট পোস্ট করা
                        comment_data = {
                            "c_name": "AUTO REPLY",
                            "c_story": "41225",
                            "c_comment": reply_text,
                            "comment_submit": "মন্তব্য করুন"
                        }

                        post_response = session.post(story_url, data=comment_data)

                        if post_response.status_code == 200:
                            print("Comment posted successfully!")
                        else:
                            print("Failed to post comment!")

        # ২০ সেকেন্ড অপেক্ষা করুন
        time.sleep(20)

# সার্ভার চালু করুন
if __name__ == "__main__":
    from threading import Thread

    # Keep alive থ্রেড চালু করুন
    Thread(target=keep_alive).start()

    # বট থ্রেড চালু করুন
    Thread(target=bot_loop).start()

    # Flask অ্যাপ চালু করুন
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
