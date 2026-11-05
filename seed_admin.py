
from app.db.session import Base, engine, SessionLocal
from app.models import Admin
from app.core.config import settings
from app.core.security import hash_password


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        email = settings.admin_email.lower()

        if settings.admin_password == "CHANGE_THIS_STRONG_PASSWORD":
            raise SystemExit(
                "Set ADMIN_PASSWORD in backend/.env before creating/resetting the admin."
            )

        admin = db.query(Admin).filter(Admin.email == email).first()

        if admin:
            admin.name = settings.admin_name
            admin.is_active = True
            admin.hashed_password = hash_password(settings.admin_password)
            db.commit()
            print(f"Admin password reset successfully: {admin.email}")
        else:
            admin = Admin(
                name=settings.admin_name,
                email=email,
                hashed_password=hash_password(settings.admin_password),
                is_active=True,
            )
            db.add(admin)
            db.commit()
            print(f"Admin created successfully: {admin.email}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
