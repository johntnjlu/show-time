from app import db

class Show(db.Model):
    __tablename__ = 'shows'

    sid = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    airing_schedules = db.relationship('AiringSchedule', backref='show')

    def to_json(self):
        return {
            "id": self.sid,
            "title": self.title,
            "airingSchedules": [schedule.to_json() for schedule in self.airing_schedules]
        }

class User(db.Model):
    __tablename__ = 'users'

    uid = db.Column(db.Integer, primary_key=True)
    time_zone = db.Column(db.String(80), nullable=False)
    followed_shows = db.relationship('Show', secondary='user_shows', backref='followers')

    def to_json(self):
        return {
            "id": self.uid,
            "timeZone": self.time_zone,
            "followedShows": [show.to_json() for show in self.followed_shows]
        }

class AiringSchedule(db.Model):
    __tablename__ = 'airing_schedules'

    asid = db.Column(db.Integer, primary_key=True)
    episode = db.Column(db.Integer, nullable=False)
    airing_at = db.Column(db.Integer, nullable=False)
    show_id = db.Column(db.Integer, db.ForeignKey('shows.sid'), nullable=False)

    def to_json(self):
        return {
            "id": self.asid,
            "episode": self.episode,
            "airingAt": self.airing_at,
            "showId": self.show_id
        }
    
    

class UserShow(db.Model):
    __tablename__ = 'user_shows'

    user_id = db.Column(db.Integer, db.ForeignKey('users.uid'), primary_key=True)
    show_id = db.Column(db.Integer, db.ForeignKey('shows.sid'), primary_key=True)



