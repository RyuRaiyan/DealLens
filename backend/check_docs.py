from app.database import SessionLocal
from app.models import Document

db = SessionLocal()

docs = db.query(Document).order_by(Document.id).all()

for d in docs:
    print("ID:", d.id)
    print("Filename:", d.filename)
    print("Characters:", len(d.content))
    print("Has CERTIFICATIONS:", "CERTIFICATIONS" in d.content.upper())
    print("Has PROJECTS:", "PROJECTS" in d.content.upper())
    print("-" * 60)

db.close()