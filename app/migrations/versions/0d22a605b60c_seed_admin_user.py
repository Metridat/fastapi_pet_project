"""Seed admin user

Revision ID: 0d22a605b60c
Revises: 4f3dee33c9d3
Create Date: 2025-11-03 20:26:17.056560

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

import os

# revision identifiers, used by Alembic.
revision: str = '0d22a605b60c'
down_revision: Union[str, Sequence[str], None] = '4f3dee33c9d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def upgrade():
    """Создаём администратора, если его ещё нет"""
    admin_email = "admin@example.com"
    admin_password = os.getenv('admin_password')
    if not admin_password:
        raise ValueError("environment admin password not found")
    admin_hashed = hash_password(admin_password)

    op.execute(f"""
        INSERT INTO users (email, hashed_password, role, is_active)
        VALUES ('{admin_email}', '{admin_hashed}', 'admin', true)
        ON CONFLICT (email) DO NOTHING;
    """)


def downgrade():
    """Удаляем администратора"""
    op.execute("""
        DELETE FROM users WHERE email='admin@example.com';
    """)
