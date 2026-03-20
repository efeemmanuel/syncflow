from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.models.company import Company
from app.models.user import User
from app.models.team import Team
from app.models.team_member import TeamMember
from app.models.project import Project
from app.models.project_team import ProjectTeam
from app.models.project_link import ProjectLink
from app.models.task import Task
from app.models.task_submission import TaskSubmission
from app.models.task_attachment import TaskAttachment
from app.models.task_comment import TaskComment
from app.models.task_integration import TaskIntegration
from app.models.channel import Channel
from app.models.channel_member import ChannelMember
from app.models.message import Message
from app.models.thread import Thread
from app.models.invitation import Invitation
from app.models.notification import Notification
from app.models.audit_log import AuditLog





''' 
Base is like a school register.
Every student (model) that signs the register (inherits from Base) gets recorded.
The teacher (Alembic/SQLAlchemy) checks the register to know who exists.




You are telling SQLAlchemy three things:

**1 — This class is a database table.**

Without inheriting from `Base`, `Company` is just a regular Python class. SQLAlchemy has no idea it exists. By inheriting from `Base`, SQLAlchemy registers it internally and says "this is a table I need to manage."

**2 — The metadata connection.**

`Base` carries a `metadata` object internally. Metadata is a collection of all your table definitions. Every class that inherits from `Base` gets added to that metadata automatically.
```
Base.metadata
    ├── companies table
    ├── users table
    ├── teams table
    └── projects table








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