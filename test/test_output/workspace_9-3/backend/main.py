from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid
from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import Schema, TEXT, ID, DATETIME
from whoosh.qparser import QueryParser
import os
from .database import SessionLocal, engine, Base
from .models import Note, Category
from .schemas import NoteCreate, NoteUpdate, NoteResponse, CategoryCreate, CategoryResponse

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Search index setup
if not os.path.exists("search_index"):
    os.mkdir("search_index")
    schema = Schema(
        id=ID(stored=True),
        title=TEXT(stored=True),
        content=TEXT(stored=True),
        category=TEXT(stored=True),
        created_at=DATETIME(stored=True),
        updated_at=DATETIME(stored=True)
    )
    ix = create_in("search_index", schema)
else:
    ix = open_dir("search_index")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/notes/", response_model=NoteResponse)
def create_note(note: NoteCreate, db = Depends(get_db)):
    db_note = Note(
        title=note.title,
        content=note.content,
        category_id=note.category_id
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    
    # Index the note
    writer = ix.writer()
    writer.add_document(
        id=str(db_note.id),
        title=db_note.title,
        content=db_note.content,
        category=db_note.category.name if db_note.category else "",
        created_at=db_note.created_at,
        updated_at=db_note.updated_at
    )
    writer.commit()
    
    return db_note

@app.get("/notes/", response_model=List[NoteResponse])
def read_notes(skip: int = 0, limit: int = 100, db = Depends(get_db)):
    return db.query(Note).offset(skip).limit(limit).all()

@app.get("/notes/{note_id}", response_model=NoteResponse)
def read_note(note_id: int, db = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@app.put("/notes/{note_id}", response_model=NoteResponse)
def update_note(note_id: int, note: NoteUpdate, db = Depends(get_db)):
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    update_data = note.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_note, key, value)
    
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    
    # Update index
    writer = ix.writer()
    writer.update_document(
        id=str(db_note.id),
        title=db_note.title,
        content=db_note.content,
        category=db_note.category.name if db_note.category else "",
        created_at=db_note.created_at,
        updated_at=db_note.updated_at
    )
    writer.commit()
    
    return db_note

@app.delete("/notes/{note_id}")
def delete_note(note_id: int, db = Depends(get_db)):
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Remove from index
    writer = ix.writer()
    writer.delete_by_term('id', str(note_id))
    writer.commit()
    
    db.delete(db_note)
    db.commit()
    return {"ok": True}

@app.get("/search/")
def search_notes(q: str):
    results = []
    with ix.searcher() as searcher:
        query = QueryParser("content", ix.schema).parse(q)
        hits = searcher.search(query, limit=20)
        for hit in hits:
            results.append({
                "id": hit["id"],
                "title": hit["title"],
                "content": hit["content"],
                "category": hit["category"],
                "created_at": hit["created_at"],
                "updated_at": hit["updated_at"]
            })
    return results

# Category endpoints
@app.post("/categories/", response_model=CategoryResponse)
def create_category(category: CategoryCreate, db = Depends(get_db)):
    db_category = Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@app.get("/categories/", response_model=List[CategoryResponse])
def read_categories(skip: int = 0, limit: int = 100, db = Depends(get_db)):
    return db.query(Category).offset(skip).limit(limit).all()