from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import sqlite3
import os

# Flask App Setup
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Database
DATABASE = 'scheduled_posts.db'

# Scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Scheduled Posting Job
def post_scheduled():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("SELECT * FROM posts WHERE scheduled_time <= ?", (now,))
    posts = cursor.fetchall()
    for post in posts:
        content, platforms, image, post_id = post[1], post[2].split(','), post[3], post[0]
        for platform in platforms:
            print(f"Posting to {platform}: {content} (Image: {image})")
            # Add platform API calls here
        cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()

scheduler.add_job(post_scheduled, 'interval', minutes=1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_post', methods=['POST'])
def submit_post():
    # Loop through all the post slots
    posts_data = []
    for i in range(5):
        content = request.form.get(f"content-{i}")
        platforms = ','.join(request.form.getlist(f"platform-{i}"))
        scheduled_time = request.form.get(f"scheduled-time-{i}")
        image = request.files.get(f"image-{i}")
        
        # Handle file upload for image
        image_filename = None
        if image:
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        # Save post details to database
        if content and platforms:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO posts (content, platforms, image, scheduled_time) VALUES (?, ?, ?, ?)",
                           (content, platforms, image_filename, scheduled_time))
            conn.commit()
            conn.close()

            posts_data.append({"message": f"Post {i + 1} submitted successfully!"})
        else:
            posts_data.append({"error": f"Post {i + 1} is missing content or platforms."})

    return jsonify(posts_data)

if __name__ == '__main__':
    app.run(debug=True)
