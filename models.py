from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class L1PromptDetail(db.Model):
    __tablename__ = 'l1promptdetails'
    
    PromptID = db.Column(db.String(50), primary_key=True)
    L1_Prompt = db.Column(db.Text, nullable=False)
    CreatedOn = db.Column(db.DateTime, default=datetime.utcnow)
    LastModifiedDate = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    IsActive = db.Column(db.String(1), default='Y')
    ClientId = db.Column(db.String(10))
    
    # Relationship with L2 prompts
    l2_prompts = db.relationship('L2PromptDetail', backref='l1_prompt', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'PromptID': self.PromptID,
            'L1_Prompt': self.L1_Prompt,
            'CreatedOn': self.CreatedOn.isoformat() if self.CreatedOn else None,
            'LastModifiedDate': self.LastModifiedDate.isoformat() if self.LastModifiedDate else None,
            'IsActive': self.IsActive,
            'ClientId': self.ClientId,
            'l2_count': len(self.l2_prompts) if self.l2_prompts else 0
        }

class L2PromptDetail(db.Model):
    __tablename__ = 'l2promptdetails'
    
    id = db.Column(db.Integer, primary_key=True)
    PromptID = db.Column(db.String(50))
    L1_PromptID = db.Column(db.String(50), db.ForeignKey('l1promptdetails.PromptID'), nullable=False)
    L2_Prompt = db.Column(db.Text, nullable=False)
    CreatedOn = db.Column(db.DateTime, default=datetime.utcnow)
    LastModifiedDate = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    IsActive = db.Column(db.String(1), default='Y')
    Model = db.Column(db.String(50))
    Priority = db.Column(db.Integer)
    ClientId = db.Column(db.String(10))
    CategoryUID = db.Column(db.String(10))
    Heading = db.Column(db.String(100))
    Subheading = db.Column(db.String(100))
    Orders = db.Column(db.String(50))
    Render = db.Column(db.String(1), default='Y')
    
    def to_dict(self):
        return {
            'id': self.id,
            'PromptID': self.PromptID,
            'L1_PromptID': self.L1_PromptID,
            'L2_Prompt': self.L2_Prompt,
            'CreatedOn': self.CreatedOn.isoformat() if self.CreatedOn else None,
            'LastModifiedDate': self.LastModifiedDate.isoformat() if self.LastModifiedDate else None,
            'IsActive': self.IsActive,
            'Model': self.Model,
            'Priority': self.Priority,
            'ClientId': self.ClientId,
            'CategoryUID': self.CategoryUID,
            'Heading': self.Heading,
            'Subheading': self.Subheading,
            'Orders': self.Orders,
            'Render': self.Render
        }