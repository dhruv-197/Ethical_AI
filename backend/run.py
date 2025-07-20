import os
from app import create_app, db
from app.models.user import User
from app.models.tweet import Tweet
from app.models.post import Post

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Tweet=Tweet, Post=Post)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)