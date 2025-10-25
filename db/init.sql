-- Initialize HealthSphere Database
CREATE DATABASE healthsphere;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE healthsphere TO postgres;
