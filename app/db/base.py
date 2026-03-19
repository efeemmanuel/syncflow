from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# import all models here so Alembic can discover them
from app.models.company import Company
from app.models.user import User
from app.models.team import Team
from app.models.project import Project
from app.models.task import Task
from app.models.message import Message
from app.models.invitation import Invitation







''' 

This section is specifically for Alembic.

When Alembic generates a migration it needs to know every table that exists in your application. It finds them by looking at everything that has inherited from `Base`.

But Python only knows about a class if it has been imported somewhere. If you never import `User` anywhere Python doesn't load that file and SQLAlchemy never registers the `User` class.

So we import every single model here in one place. When Alembic runs it imports `base.py`, which triggers all these imports, which registers all models with `Base`, which gives Alembic the full picture of your database.

**A common mistake beginners make:**

You add a new model — say `Notification` — write the file, but forget to add it here. You run Alembic to generate a migration. Alembic doesn't see `Notification`. No migration gets generated for it. You wonder why your table doesn't exist in the database.

The fix is always — add every new model to this file.

---

**The relationship between the three db files:**
```
base.py
  → defines Base class
  → imports all models

session.py
  → creates async engine using DATABASE_URL
  → creates AsyncSessionLocal factory
  → get_db() gives routes a database session

models/ (coming next)
  → every model inherits from Base
  → Base was defined in base.py
  → session.py connects them to PostgreSQL


'''