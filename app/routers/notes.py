from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas, auth
from app.database import get_db

router = APIRouter(prefix="/notes", tags=["notes"])

@router.get("/", response_model=List[schemas.NoteOut])
def get_notes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_user)
):
    notes = db.query(models.Note).filter(
        models.Note.user_id == current_user.id,
        models.Note.is_archived == False
    ).offset(skip).limit(limit).all()
    return notes

@router.get("/archived", response_model=List[schemas.NoteOut])
def get_archived_notes(
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_user)
):
    notes = db.query(models.Note).filter(
        models.Note.user_id == current_user.id,
        models.Note.is_archived == True
    ).all()
    return notes

@router.get("/{note_id}", response_model=schemas.NoteOut)
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_user)
):
    note = db.query(models.Note).filter(
        models.Note.id == note_id,
        models.Note.user_id == current_user.id
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.post("/", response_model=schemas.NoteOut, status_code=status.HTTP_201_CREATED)
def create_note(
    note: schemas.NoteCreate,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_user)
):
    db_note = models.Note(
        title=note.title,
        content=note.content,
        user_id=current_user.id
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

@router.put("/{note_id}", response_model=schemas.NoteOut)
def update_note(
    note_id: int,
    note_update: schemas.NoteUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_user)
):
    note = db.query(models.Note).filter(
        models.Note.id == note_id,
        models.Note.user_id == current_user.id
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    if note_update.title is not None:
        note.title = note_update.title
    if note_update.content is not None:
        note.content = note_update.content
    if note_update.is_archived is not None:
        note.is_archived = note_update.is_archived
    
    db.commit()
    db.refresh(note)
    return note

@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_user)
):
    note = db.query(models.Note).filter(
        models.Note.id == note_id,
        models.Note.user_id == current_user.id
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    db.delete(note)
    db.commit()
    return None