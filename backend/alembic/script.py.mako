<%!
from alembic import op
import sqlalchemy as sa
%>

"""A generic, single-file template for Alembic migration scripts.
"""

revision = '${REVISION}'
down_revision = ${DOWN_REVISION}
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    pass


def downgrade():
    pass
