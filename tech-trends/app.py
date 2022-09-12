import sqlite3
import logging

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort


#logging.basicConfig(level=logging.DEBUG, filename='myapp.log', format='%(asctime)s %(levelname)s:%(message)s')
# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection


# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                              (post_id,)).fetchone()
    connection.close()
    return post


def count_connections():
    log_file = 'myapp.log'
    db_connections = []
    with open(log_file) as file:
        file = file.readlines()

    for line in file:
        if "DatabaseConnection" in line:
            db_connections.append(line)

    conn = len(db_connections)
    return conn


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'


# Define the main route of the web application
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    logging.info("DatabaseConnection")
    connection.close()
    logging.info("Loaded main page")
    return render_template('index.html', posts=posts)


# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    logging.info("DatabaseConnection")
    if post is None:
        logging.info("No post with this ID")
        return render_template('404.html'), 404
    else:
        return render_template('post.html', post=post)


# Define the About Us page
@app.route('/about')
def about():
    logging.info("Loaded ABOUT page")
    return render_template('about.html')


# Define the post creation functionality
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
            logging.info("No title provided to create post")
        else:
            connection = get_db_connection()
            logging.info("DatabaseConnection")
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                               (title, content))
            connection.commit()
            logging.info("Post created")
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')


@app.route("/healthz")
def status():
    response = app.response_class(
        response=json.dumps({"result": "OK - Healthy"}),
        status=200,
        mimetype="application/json"
    )
    app.logger.info("HEALTH: Status Requested")
    return response


@app.route("/metrics")
def metrics():
    """metrics endpoint"""
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    conn = count_connections()
    response = app.response_class(response=json.dumps({"db_connection_count": conn, "post_count": len(posts)}),
                                  status=200,
                                  mimetype="application/json"
                                  )

    app.logger.info("Metrics Requested")

    return response


# start the application on port 3111
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s',
                        handlers=[logging.FileHandler('myapp.log'), logging.StreamHandler()])
    #logging.getLogger().addHandler(logging.StreamHandler())
    app.run(host='0.0.0.0', port='3111', debug=True)
