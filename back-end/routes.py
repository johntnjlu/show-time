from flask import request, jsonify
from app import app, db, login_manager
from models import User, AiringSchedule, Show
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from scraper import get_release_times

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/create_user", methods=["POST"])
def create_contact():
    email = request.json.get("email")
    password = request.json.get("password")
    time_zone = request.json.get("timeZone")

    if not email or not password or not time_zone:
        return (
            jsonify({"message": "You must include email, password, and time zone"}),
            400,
        )

    new_user = User(email=email,password=password, time_zone=time_zone)

    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        return jsonify({"message": str(e)}), 400

    return jsonify({"message": "User created!"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if not user or user.password != password:
        return jsonify({"message": "Invalid email or password"}), 401
    
    login_user(user)
    return jsonify({"message": "Login successful", "user": user.to_json()})

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"})

@app.route("/users/shows", methods=["GET"])
@login_required
def get_user_shows():
    followed_shows = [show.to_json() for show in current_user.followed_shows]
    return jsonify({"user_id": current_user.uid, "followed_shows": followed_shows})


@app.route("/add_show/<string:anime_title>", methods=["PATCH"])
@login_required
def add_show(anime_title):
    shows_data = get_release_times(anime_title)
    
    if not shows_data:
        return jsonify({"message": f"No airing schedule found for '{anime_title}'"}), 404

    show_title = shows_data[0]["title"]
    airing_schedules = shows_data

    existing_show = Show.query.filter_by(title=show_title).first()
    
    # airing schedule of existing_show has not been added yet
    if not existing_show:
        new_show = Show(title=show_title)
        db.session.add(new_show)
        db.session.flush()

        for schedule in airing_schedules:
            new_airing_schedule = AiringSchedule(
                episode=schedule["episode"],
                airing_at=schedule["airing_at"],
                show_id=new_show.sid,
            )
            db.session.add(new_airing_schedule)

        db.session.commit()

        current_user.followed_shows.append(new_show)
        db.session.commit()

        return jsonify({"message": f"Show '{show_title}' added to the database and followed shows"}), 201

    # airing schedule already exists for show, so we just add it to the user's followed shows
    if existing_show not in current_user.followed_shows:
        current_user.followed_shows.append(existing_show)
        db.session.commit()
        return jsonify({"message": f"Show '{show_title}' added to your followed shows"}), 200

    return jsonify({"message": f"Show '{show_title}' is already in your followed shows"}), 200
    

@app.route("/delete_show/<string:anime_title>", methods=["DELETE"])
@login_required
def delete_show(anime_title):
    show_to_delete = Show.query.filter_by(title=anime_title).first()

    if not show_to_delete:
        return jsonify({"message": f"Show '{anime_title}' not found in the database"}), 404

    if show_to_delete in current_user.followed_shows:
        current_user.followed_shows.remove(show_to_delete)
        db.session.commit()
        
        return jsonify({"message": f"Show '{anime_title}' removed from your followed shows"}), 200

    return jsonify({"message": f"Show '{anime_title}' is not in your followed shows"}), 404

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)