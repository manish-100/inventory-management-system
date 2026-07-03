"""initial schema

Revision ID: 001_initial
Revises:
Create Date: 2026-07-02
"""
from alembic import op
import sqlalchemy as sa

revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('products',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('sku', sa.String(length=80), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Numeric(10, 2), nullable=False),
        sa.Column('stock', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('sku')
    )
    op.create_index('ix_products_id', 'products', ['id'])
    op.create_index('ix_products_sku', 'products', ['sku'])

    op.create_table('customers',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('email', sa.String(length=150), nullable=False),
        sa.Column('phone', sa.String(length=30), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_customers_id', 'customers', ['id'])
    op.create_index('ix_customers_email', 'customers', ['email'])

    op.create_table('orders',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('customer_id', sa.Integer(), sa.ForeignKey('customers.id'), nullable=False),
        sa.Column('total_amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='PLACED'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    op.create_index('ix_orders_id', 'orders', ['id'])

    op.create_table('order_items',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('order_id', sa.Integer(), sa.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Numeric(10, 2), nullable=False)
    )
    op.create_index('ix_order_items_id', 'order_items', ['id'])

def downgrade():
    op.drop_index('ix_order_items_id', table_name='order_items')
    op.drop_table('order_items')
    op.drop_index('ix_orders_id', table_name='orders')
    op.drop_table('orders')
    op.drop_index('ix_customers_email', table_name='customers')
    op.drop_index('ix_customers_id', table_name='customers')
    op.drop_table('customers')
    op.drop_index('ix_products_sku', table_name='products')
    op.drop_index('ix_products_id', table_name='products')
    op.drop_table('products')
