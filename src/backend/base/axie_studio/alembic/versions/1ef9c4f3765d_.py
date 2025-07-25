"""


Revision ID: 1ef9c4f3765d
Revises: fd531f8868b1
Create Date: 2023-12-04 15:00:27.968998

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.engine.reflection import Inspector

from axie_studio.utils import migration

# revision identifiers, used by Alembic.
revision: str = "1ef9c4f3765d"
down_revision: Union[str, None] = "fd531f8868b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    # ### commands auto generated by Alembic - please adjust! ###
    inspector = sa.inspect(conn)  # type: ignore
    # ### commands auto generated by Alembic - please adjust! ###

    with op.batch_alter_table("apikey", schema=None) as batch_op:
        if migration.column_exists(table_name="apikey", column_name="name", conn=conn):
            api_key_columns = inspector.get_columns("apikey")
            name_column = next((column for column in api_key_columns if column["name"] == "name"), None)
            if name_column is not None and isinstance(name_column["type"], sa.VARCHAR) and not name_column["nullable"]:
                batch_op.alter_column("name", existing_type=sa.VARCHAR(), nullable=True)

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    conn = op.get_bind()
    inspector = sa.inspect(conn)  # type: ignore

    with op.batch_alter_table("apikey", schema=None) as batch_op:
        if migration.column_exists(table_name="apikey", column_name="name", conn=conn):
            api_key_columns = inspector.get_columns("apikey")
            name_column = next((column for column in api_key_columns if column["name"] == "name"), None)
            if name_column is not None and isinstance(name_column["type"], sa.VARCHAR) and name_column["nullable"]:
                batch_op.alter_column("name", existing_type=sa.VARCHAR(), nullable=False)

    # ### end Alembic commands ###
