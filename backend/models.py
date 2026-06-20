# A model is simply a database table represented as a Python class

from datetime import datetime
from extensions import db

class RemoteLab(db.Model):

    __tablename__ = "remote_lab"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))

    stream_url = db.Column(db.String(255))





class ROIConfig(db.Model):

    __tablename__ = "roi_config"

    id = db.Column(db.Integer, primary_key=True)

    r_lab_id = db.Column(db.Integer, db.ForeignKey("remote_lab.id"))

    name = db.Column(db.String(100), nullable=False)
    
    x = db.Column(db.Float)
    y = db.Column(db.Float)

    width = db.Column(db.Float)
    height = db.Column(db.Float)





class StreamLog(db.Model):

    __tablename__ = "stream_log"

    id = db.Column(db.Integer, primary_key=True)

    r_lab_id = db.Column(db.Integer, db.ForeignKey("remote_lab.id"))

    bitrate = db.Column(db.Float)

    buffer_level = db.Column(db.Float)

    throughput = db.Column(db.Float)

    latency = db.Column(db.Float)

    timestamp = db.Column(db.DateTime, default = datetime.utcnow)

    ##### Will be the user session, for now it is not that important but will be during intergration. Then set it to not be nullable
    session = db.Column(db.Integer)





class RLDecisionLog(db.Model):
    __tablename__ = "rl_decision_log"

    id = db.Column(db.Integer, primary_key=True)

    r_lab_id = db.Column(
        db.Integer,
        db.ForeignKey("remote_lab.id")
    )

    selected_bitrate = db.Column(db.Float)

    reward = db.Column(db.Float)

    timestamp = db.Column(db.DateTime, default = datetime.utcnow)