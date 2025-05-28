from fastapi import FastAPI, HTTPException, Body, Query
from typing import List, Optional
import uvicorn
import os
from pathlib import Path
from git import Repo
import uuid
import datetime

# ----- Settings -----
REPO_PATH = "./repo"
HOST = "0.0.0.0"
PORT = 8000
DEBUG = True

# ----- App Setup -----
app = FastAPI(title="Markdown Notes MCP", description="Notes with UUIDs, dates, and Git versioning in Markdown.", version="3.0")

# Initialize Git repo
if not os.path.exists(REPO_PATH):
    os.makedirs(REPO_PATH)
    repo = Repo.init(REPO_PATH)
else:
    repo = Repo(REPO_PATH)

notes_dir = Path(REPO_PATH) / "notes"
notes_dir.mkdir(parents=True, exist_ok=True)

# ----- Core Functions -----
def format_note(note_uuid: str, content: str, tags: Optional[List[str]], author: Optional[str], last_updated: str):
    metadata = f"""---
note_uuid: {note_uuid}
last_updated: {last_updated}
tags: {', '.join(tags) if tags else 'None'}
author: {author or 'Unknown'}
---

"""
    return metadata + content

def parse_metadata(note_text: str):
    lines = note_text.splitlines()
    metadata = {}
    if lines[0] == "---":
        for i, line in enumerate(lines[1:], start=1):
            if line == "---":
                break
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()
    return metadata

def get_note_path(note_id: str):
    return notes_dir / f"{note_id}.md"

def commit_changes(message: str):
    commit_uuid = str(uuid.uuid4())
    repo.index.commit(f"{message} (Commit UUID: {commit_uuid})")
    return commit_uuid

# ----- API Endpoints -----
@app.post("/notes", summary="Add a new markdown note with UUIDs, tags, and author")
async def add_note(content: str = Body(...), tags: Optional[List[str]] = Query(None), author: Optional[str] = Query(None)):
    note_uuid = str(uuid.uuid4())
    last_updated = datetime.datetime.utcnow().isoformat()
    formatted_content = format_note(note_uuid, content, tags, author, last_updated)
    note_path = get_note_path(note_uuid)
    note_path.write_text(formatted_content)
    repo.index.add([str(note_path)])
    commit_uuid = commit_changes(f"Add note {note_uuid}")
    return {"note_uuid": note_uuid, "commit_uuid": commit_uuid, "last_updated": last_updated}

@app.get("/notes/{note_uuid}", summary="Get a note by UUID")
async def get_note(note_uuid: str):
    note_path = get_note_path(note_uuid)
    if not note_path.exists():
        raise HTTPException(status_code=404, detail="Note not found")
    content = note_path.read_text()
    return {"note_uuid": note_uuid, "content": content}

@app.put("/notes/{note_uuid}", summary="Update an existing note with new content, tags, or author")
async def update_note(note_uuid: str, content: str = Body(...), tags: Optional[List[str]] = Query(None), author: Optional[str] = Query(None)):
    note_path = get_note_path(note_uuid)
    if not note_path.exists():
        raise HTTPException(status_code=404, detail="Note not found")
    last_updated = datetime.datetime.utcnow().isoformat()
    formatted_content = format_note(note_uuid, content, tags, author, last_updated)
    note_path.write_text(formatted_content)
    repo.index.add([str(note_path)])
    commit_uuid = commit_changes(f"Update note {note_uuid}")
    return {"note_uuid": note_uuid, "commit_uuid": commit_uuid, "last_updated": last_updated}

@app.delete("/notes/{note_uuid}", summary="Delete a note by UUID")
async def delete_note(note_uuid: str):
    note_path = get_note_path(note_uuid)
    if note_path.exists():
        note_path.unlink()
        repo.index.remove([str(note_path)])
        commit_uuid = commit_changes(f"Delete note {note_uuid}")
        return {"detail": f"Note {note_uuid} deleted", "commit_uuid": commit_uuid}
    else:
        raise HTTPException(status_code=404, detail="Note not found")

@app.get("/notes", summary="List all notes with metadata")
async def list_notes():
    notes = []
    for note_file in notes_dir.glob("*.md"):
        content = note_file.read_text()
        metadata = parse_metadata(content)
        notes.append({
            "note_uuid": metadata.get("note_uuid", "unknown"),
            "last_updated": metadata.get("last_updated", "unknown"),
            "tags": metadata.get("tags", "unknown"),
            "author": metadata.get("author", "unknown")
        })
    return notes

@app.get("/search", summary="Search notes by keyword, tag, or author")
async def search_notes(keyword: Optional[str] = Query(None), tag: Optional[str] = Query(None), author: Optional[str] = Query(None)):
    results = []
    for note_file in notes_dir.glob("*.md"):
        content = note_file.read_text()
        metadata = parse_metadata(content)
        if (not keyword or keyword.lower() in content.lower()) and \
           (not tag or tag in metadata.get("tags", "")) and \
           (not author or author == metadata.get("author", "")):
            results.append({
                "note_uuid": metadata.get("note_uuid"),
                "content": content,
                "last_updated": metadata.get("last_updated"),
                "tags": metadata.get("tags"),
                "author": metadata.get("author")
            })
    return results

@app.get("/notes/{note_uuid}/history", summary="Get version history of a note")
async def note_history(note_uuid: str):
    note_path = str(get_note_path(note_uuid))
    commits = list(repo.iter_commits(paths=note_path))
    history = [{"commit_uuid": c.hexsha, "message": c.message.strip(), "date": c.committed_datetime.isoformat()} for c in commits]
    return {"note_uuid": note_uuid, "history": history}

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
