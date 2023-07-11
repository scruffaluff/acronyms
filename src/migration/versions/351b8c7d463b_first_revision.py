"""First revision

Revision ID: 351b8c7d463b
Revises: 
Create Date: 2022-10-22 10:19:25.941686

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "351b8c7d463b"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "acronyms",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("abbreviation", sa.Unicode(), nullable=True),
        sa.Column("phrase", sa.Unicode(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("abbreviation", "phrase"),
    )
    op.create_index(op.f("ix_acronyms_id"), "acronyms", ["id"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_acronyms_id"), table_name="acronyms")
    op.drop_table("acronyms")
    # ### end Alembic commands ###