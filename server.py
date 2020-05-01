from flask import Flask

from db import User

app = Flask(__name__)

@app.route('/users', methods=["GET", "POST"])
def users():
    users = db.select()
    print(users)
    return {"users": users}

if __name__ == '__main__':
    db = User()
    app.run()