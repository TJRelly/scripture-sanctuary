\c scripture-sanctuary
-- Drop the association table first to avoid foreign key constraint issues
DROP TABLE IF EXISTS favorite_tags CASCADE;

-- Drop the favorites table, which may have foreign key constraints referencing the tags table
DROP TABLE IF EXISTS favorites CASCADE;

-- Drop the tags table
DROP TABLE IF EXISTS tags CASCADE;

-- Drop the users table
DROP TABLE IF EXISTS users CASCADE;
