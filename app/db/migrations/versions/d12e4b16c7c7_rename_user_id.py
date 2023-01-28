"""rename_user_id

Revision ID: d12e4b16c7c7
Revises: 13bd9f24b789
Create Date: 2022-06-13 21:51:59.481371

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "d12e4b16c7c7"
down_revision = "13bd9f24b789"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("match_confirmations", sa.Column("player_id", postgresql.UUID(as_uuid=True), nullable=False))
    op.drop_constraint(op.f("fk_match_confirmations_user_id_users"), "match_confirmations", type_="foreignkey")
    op.create_foreign_key(
        op.f("fk_match_confirmations_player_id_users"), "match_confirmations", "users", ["player_id"], ["id"]
    )
    op.drop_column("match_confirmations", "user_id")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("match_confirmations", sa.Column("user_id", postgresql.UUID(), autoincrement=False, nullable=False))
    op.drop_constraint(op.f("fk_match_confirmations_player_id_users"), "match_confirmations", type_="foreignkey")
    op.create_foreign_key(
        op.f("fk_match_confirmations_user_id_users"), "match_confirmations", "users", ["user_id"], ["id"]
    )
    op.drop_column("match_confirmations", "player_id")
    # ### end Alembic commands ###
