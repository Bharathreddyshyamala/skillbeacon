from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.skill import Skill


DEFAULT_SKILLS = [
    (
        "Python",
        "Programming",
        "Python programming language",
    ),
    (
        "Java",
        "Programming",
        "Java programming language",
    ),
    (
        "JavaScript",
        "Programming",
        "JavaScript programming language",
    ),
    (
        "SQL",
        "Database",
        "Structured Query Language",
    ),
    (
        "FastAPI",
        "Backend",
        "Python API framework",
    ),
    (
        "Django",
        "Backend",
        "Python web framework",
    ),
    (
        "Spring Boot",
        "Backend",
        "Java backend framework",
    ),
    (
        "React",
        "Frontend",
        "Frontend JavaScript library",
    ),
    (
        "Next.js",
        "Frontend",
        "React web framework",
    ),
    (
        "PostgreSQL",
        "Database",
        "Relational database",
    ),
    (
        "MongoDB",
        "Database",
        "Document database",
    ),
    (
        "Redis",
        "Database",
        "In-memory data store",
    ),
    (
        "Docker",
        "DevOps",
        "Containerization platform",
    ),
    (
        "Kubernetes",
        "DevOps",
        "Container orchestration platform",
    ),
    (
        "Git",
        "Development Tools",
        "Version control system",
    ),
    (
        "AWS",
        "Cloud",
        "Amazon Web Services",
    ),
    (
        "Machine Learning",
        "Artificial Intelligence",
        "Machine learning concepts and tools",
    ),
    (
        "RAG",
        "Artificial Intelligence",
        "Retrieval-Augmented Generation",
    ),
]


def main():
    db = SessionLocal()

    try:
        created = 0

        for name, category, description in DEFAULT_SKILLS:
            existing = db.scalar(
                select(Skill).where(
                    Skill.name == name
                )
            )

            if existing:
                continue

            db.add(
                Skill(
                    name=name,
                    category=category,
                    description=description,
                )
            )

            created += 1

        db.commit()

        print(
            f"Skill seeding complete. "
            f"Created {created} new skills."
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()