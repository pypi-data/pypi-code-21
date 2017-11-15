from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

def get_or_create_db(cls, db_path, db_file, name=__name__):
    if not db_file.endswith('.db'):
        db_file += '.db'
    full_path = Path(db_path) / db_file    
    app = Flask(name)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////'+str(full_path.absolute())
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = SQLAlchemy(app)
    if not full_path.exists():    
        cls.get_db_model(db)
        db.create_all()
    return db

