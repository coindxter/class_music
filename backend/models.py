# SQLAlchemy models

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ClassPeriod(db.Model):
    __tablename__ = 'class_periods'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    students = db.relationship('Student', backref='class_period', cascade='all, delete-orphan')

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class_periods.id'), nullable=False)
    artists = db.relationship('Artist', backref='student', cascade='all, delete-orphan')

class Artist(db.Model):
    __tablename__ = 'artists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    songs = db.relationship('Song', backref='artist', cascade='all, delete-orphan')

class Song(db.Model):
    __tablename__ = 'songs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
