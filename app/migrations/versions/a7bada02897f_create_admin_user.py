"""Create_admin_user

Revision ID: a7bada02897f
Revises: 0ecf698de475
Create Date: 2025-12-11 17:31:58.928317

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

import os

# revision identifiers, used by Alembic.
revision: str = 'a7bada02897f'
down_revision: Union[str, Sequence[str], None] = '0ecf698de475'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def upgrade():
    """Создаём администратора, если его ещё нет"""
    admin_email = os.getenv('ADMIN_EMAIL')
    admin_password = os.getenv('ADMIN_PASSWORD')
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
