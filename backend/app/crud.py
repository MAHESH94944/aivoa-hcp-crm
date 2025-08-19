from sqlalchemy.orm import Session
from . import models, schemas
from typing import List

def get_interaction(db: Session, interaction_id: int):
    return db.query(models.HCPInteraction).filter(models.HCPInteraction.id == interaction_id).first()

def get_all_interactions(db: Session, skip: int = 0, limit: int = 100) -> List[models.HCPInteraction]:
    return db.query(models.HCPInteraction).offset(skip).limit(limit).all()

def create_interaction(db: Session, interaction: schemas.InteractionCreate) -> models.HCPInteraction:
    db_interaction = models.HCPInteraction(**interaction.model_dump())
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)
    return db_interaction