-- Sample data for development and testing

-- Sample users
INSERT INTO users (username, email, hashed_password, first_name, last_name, is_active)
VALUES
    ('john_doe', 'john@example.com', 'hashed_pass_1', 'John', 'Doe', true),
    ('jane_smith', 'jane@example.com', 'hashed_pass_2', 'Jane', 'Smith', true),
    ('bob_wilson', 'bob@example.com', 'hashed_pass_3', 'Bob', 'Wilson', true);

-- Sample products
INSERT INTO products (name, description, category, subcategory, price, average_rating, review_count, tags)
VALUES
    ('Wireless Headphones', 'High-quality wireless headphones with noise cancellation', 'Electronics', 'Audio', 79.99, 4.5, 120, '["wireless", "headphones", "noise-cancellation"]'),
    ('USB-C Cable', 'Durable USB-C charging cable', 'Electronics', 'Cables', 12.99, 4.2, 45, '["cable", "usb-c", "charging"]'),
    ('Phone Case', 'Protective phone case', 'Accessories', 'Phone', 19.99, 4.0, 89, '["case", "protection", "durable"]'),
    ('Screen Protector', 'Tempered glass screen protector', 'Accessories', 'Phone', 9.99, 4.3, 156, '["screen", "protector", "glass"]'),
    ('Portable Charger', '20000mAh portable charger', 'Electronics', 'Power', 34.99, 4.6, 203, '["charger", "portable", "battery"]'),
    ('Laptop Stand', 'Adjustable laptop stand', 'Office', 'Accessories', 44.99, 4.4, 67, '["stand", "laptop", "adjustable"]');

-- Sample interactions
INSERT INTO user_product_interactions (user_id, product_id, interaction_type, rating, interaction_weight)
VALUES
    (1, 1, 'view', NULL, 1.0),
    (1, 1, 'click', NULL, 2.0),
    (1, 1, 'add_to_cart', NULL, 3.0),
    (1, 1, 'purchase', 5.0, 5.0),
    (1, 2, 'view', NULL, 1.0),
    (1, 3, 'view', NULL, 1.0),
    (2, 1, 'view', NULL, 1.0),
    (2, 4, 'purchase', 5.0, 5.0),
    (2, 5, 'view', NULL, 1.0),
    (3, 2, 'purchase', 4.0, 5.0),
    (3, 6, 'view', NULL, 1.0);
