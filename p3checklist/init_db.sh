#!/bin/bash

# Connect to the PostgreSQL database
PGPASSWORD=p3checkpass psql -U p3checkuser -h localhost -p 5432 -d p3checklist <<EOSQL

-- Drop the table if it exists
DROP TABLE IF EXISTS main_data;

-- Create the table
CREATE TABLE main_data (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    shift VARCHAR(2) NOT NULL,
    acknowledged BOOLEAN NOT NULL DEFAULT FALSE,
    checkin BOOLEAN NOT NULL DEFAULT FALSE
);

-- Initialize the table with the last 3 days of data
INSERT INTO main_data (date, shift, acknowledged, checkin)
SELECT current_date - interval '1 day', 'AM', TRUE, TRUE UNION ALL
SELECT current_date - interval '1 day', 'ND', TRUE, TRUE UNION ALL
SELECT current_date - interval '2 day', 'AM', TRUE, TRUE UNION ALL
SELECT current_date - interval '2 day', 'ND', TRUE, TRUE UNION ALL
SELECT current_date - interval '3 day', 'AM', TRUE, TRUE UNION ALL
SELECT current_date - interval '3 day', 'ND', TRUE, TRUE;

EOSQL

echo "Database table 'main_data' dropped, recreated, and initialized."
