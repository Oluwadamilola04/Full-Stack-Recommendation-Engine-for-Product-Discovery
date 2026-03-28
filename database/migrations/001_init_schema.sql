-- Database schema migrations for E-commerce Recommendation System

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    source_id BIGINT,
    prod_id INTEGER,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    category_raw TEXT,
    brand VARCHAR(255),
    subcategory VARCHAR(100),
    price FLOAT,
    tags JSONB,
    average_rating FLOAT DEFAULT 0.0,
    review_count INTEGER DEFAULT 0,
    image_urls JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_products_prod_id ON products(prod_id);
CREATE INDEX IF NOT EXISTS idx_products_source_id ON products(source_id);
CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand);

-- User-Product Interactions table
CREATE TABLE IF NOT EXISTS user_product_interactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    interaction_type VARCHAR(50) NOT NULL,
    rating FLOAT,
    interaction_weight FLOAT DEFAULT 1.0,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Recommendation Cache table
CREATE TABLE IF NOT EXISTS recommendation_cache (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    recommendation_type VARCHAR(50) NOT NULL,
    product_ids JSONB NOT NULL,
    scores JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_subcategory ON products(subcategory);
CREATE INDEX IF NOT EXISTS idx_interactions_user_id ON user_product_interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_interactions_product_id ON user_product_interactions(product_id);
CREATE INDEX IF NOT EXISTS idx_interactions_timestamp ON user_product_interactions(timestamp);
CREATE INDEX IF NOT EXISTS idx_recommendation_cache_user_id ON recommendation_cache(user_id);
CREATE INDEX IF NOT EXISTS idx_recommendation_cache_expires_at ON recommendation_cache(expires_at);
