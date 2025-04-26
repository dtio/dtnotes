from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Date, String, Boolean, Integer

db = SQLAlchemy()

class MainData(db.Model): # Changed ShiftData to MainData
    __tablename__ = 'main_data'
    id = db.Column(Integer, primary_key=True)
    date = db.Column(Date, nullable=False, unique=True)
    shift = db.Column(String(2), nullable=False)
    acknowledged = db.Column(Boolean, nullable=False, default=False)
    checkin = db.Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<MainData(date={self.date}, shift={self.shift}, acknowledged={self.acknowledged}, checkin={self.checkin})>' #Changed ShiftData to MainData

