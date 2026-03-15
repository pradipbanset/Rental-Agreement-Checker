"""Add user_id to documents

Revision ID: 4d38e0697a16
Revises: 4560d5a51211
Create Date: 2026-01-07 XX:XX:XX.XXXXXX

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '4d38e0697a16'
down_revision = '4560d5a51211'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = inspect(conn)

    # Create enums only if they don't exist
    if 'risklevel' not in inspector.get_enums():
        risklevel = postgresql.ENUM('LOW', 'MEDIUM', 'HIGH', name='risklevel')
        risklevel.create(conn, checkfirst=True)

    if 'documentstatus' not in inspector.get_enums():
        documentstatus = postgresql.ENUM(
            'UPLOADED', 'PROCESSING', 'COMPLETED', 'ERROR', name='documentstatus'
        )
        documentstatus.create(conn, checkfirst=True)

    # Drop analyses table if exists (safe for Postgres)
    if 'analyses' in inspector.get_table_names():
        op.drop_table('analyses')

    # Create new analysis table
    op.create_table(
        'analysis',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('document_id', sa.String(), nullable=False),
        sa.Column('total_clauses', sa.Integer(), nullable=True),
        sa.Column('illegal_clauses', sa.Integer(), nullable=True),
        sa.Column('high_risk_clauses', sa.Integer(), nullable=True),
        sa.Column('medium_risk_clauses', sa.Integer(), nullable=True),
        sa.Column(
            'risk_level',
            postgresql.ENUM('LOW', 'MEDIUM', 'HIGH', name='risklevel', create_type=False),
            nullable=True,
        ),
        sa.Column('rent_amount', sa.Integer(), nullable=True),
        sa.Column('bond_amount', sa.Integer(), nullable=True),
        sa.Column('clauses', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id']),
    )
    op.create_index(op.f('ix_analysis_id'), 'analysis', ['id'], unique=False)

    # CHAT_HISTORY fixes
    op.alter_column('chat_history', 'document_id', existing_type=sa.VARCHAR(), nullable=False)

    # Clean invalid user_id data
    conn.execute(sa.text("""
        UPDATE chat_history 
        SET user_id = 1 
        WHERE user_id !~ '^[0-9]+$' OR user_id IS NULL OR user_id = 'default'
    """))

    # Convert user_id to INTEGER safely
    conn.execute(sa.text(
        "ALTER TABLE chat_history ALTER COLUMN user_id TYPE INTEGER USING user_id::integer"
    ))
    op.alter_column('chat_history', 'user_id', existing_type=sa.Integer(), nullable=False)
    op.create_index(op.f('ix_chat_history_id'), 'chat_history', ['id'], unique=False)

    # Drop old foreign keys safely
    for fk in ['chat_history_document_id_fkey', 'chat_history_user_id_fkey']:
        if fk in [c['name'] for c in inspector.get_foreign_keys('chat_history')]:
            op.drop_constraint(fk, 'chat_history', type_='foreignkey')

    # Add foreign keys
    op.create_foreign_key('chat_history_user_id_fkey', 'chat_history', 'users', ['user_id'], ['id'])
    op.create_foreign_key('chat_history_document_id_fkey', 'chat_history', 'documents', ['document_id'], ['id'])

    # DOCUMENTS table changes
    op.add_column('documents', sa.Column('uploaded_at', sa.DateTime(), nullable=True))
    op.add_column('documents', sa.Column('user_id', sa.Integer(), nullable=True))

    conn.execute(sa.text("UPDATE documents SET user_id = 1 WHERE user_id IS NULL"))
    conn.execute(sa.text("UPDATE documents SET uploaded_at = NOW() WHERE uploaded_at IS NULL"))

    op.alter_column('documents', 'user_id', nullable=False)
    op.create_index(op.f('ix_documents_user_id'), 'documents', ['user_id'], unique=False)
    op.create_foreign_key('documents_user_id_fkey', 'documents', 'users', ['user_id'], ['id'])

    # Drop old columns safely
    for col in ['updated_at', 'created_at']:
        if col in [c['name'] for c in inspector.get_columns('documents')]:
            op.drop_column('documents', col)

    # USERS table changes
    try:
        op.alter_column('users', 'created_at', existing_type=postgresql.TIMESTAMP(timezone=True),
                        type_=sa.DateTime(), existing_nullable=True)
    except:
        pass

    # Drop password column if exists
    if 'password' in [c['name'] for c in inspector.get_columns('users')]:
        op.drop_column('users', 'password')


def downgrade():
    # Add back dropped columns / constraints
    op.add_column('users', sa.Column('password', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.alter_column('users', 'created_at', existing_type=sa.DateTime(),
                    type_=postgresql.TIMESTAMP(timezone=True), existing_nullable=True)

    op.add_column('documents', sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=True))
    op.add_column('documents', sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=True))
    op.drop_constraint('documents_user_id_fkey', 'documents', type_='foreignkey')
    op.drop_index(op.f('ix_documents_user_id'), table_name='documents')
    op.drop_column('documents', 'user_id')
    op.drop_column('documents', 'uploaded_at')
    op.drop_constraint('chat_history_document_id_fkey', 'chat_history', type_='foreignkey')
    op.drop_constraint('chat_history_user_id_fkey', 'chat_history', type_='foreignkey')
    op.drop_index(op.f('ix_chat_history_id'), table_name='chat_history')
    op.alter_column('chat_history', 'user_id', existing_type=sa.Integer(),
                    type_=sa.VARCHAR(), existing_nullable=False, nullable=True)
    op.alter_column('chat_history', 'document_id', existing_type=sa.VARCHAR(), nullable=True)
    op.drop_index(op.f('ix_analysis_id'), table_name='analysis')
    op.drop_table('analysis')
