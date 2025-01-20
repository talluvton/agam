CREATE TABLE IF NOT EXISTS users (
    id serial primary key,  
    username varchar(50) NOT NULL,
    hashed_password varchar(200) NOT NULL
);

CREATE TABLE IF NOT EXISTS employers (
    id serial primary key, 
    employer_name varchar(50) NOT NULL,
    government_id bigint NOT NULL,
    created_by_user_id int,
    foreign key (created_by_user_id) references users(id) 
);

CREATE TABLE IF NOT EXISTS employees (
    id serial primary key,  
    first_name varchar(50) NOT NULL,
    last_name varchar(50) NOT NULL,
    position varchar(50) NOT NULL,
    government_id integer NOT NULL,  
    employer_id integer,  
    created_by_user_id integer,
    foreign key (employer_id) references employers(id),
    foreign key (created_by_user_id) references users(id) 
);

-- functions
CREATE OR REPLACE FUNCTION is_table_empty(table_name TEXT)
RETURNS BOOLEAN AS $$
DECLARE
    count_result INTEGER;
BEGIN
    EXECUTE format('SELECT COUNT(*) FROM %I', table_name) INTO count_result;

    RETURN count_result = 0;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_user_by_username(p_username VARCHAR)
RETURNS TABLE(
    id INTEGER,
    username VARCHAR(50),
    hashed_password VARCHAR(200)
) AS $$
BEGIN
    RETURN QUERY
    SELECT u.id, u.username, u.hashed_password
    FROM users u
    WHERE u.username = p_username;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION insert_user(
    p_username VARCHAR(50),
    p_hashed_password VARCHAR(200)
)
RETURNS void AS $$
BEGIN
    INSERT INTO users (username, hashed_password)
    VALUES (p_username, p_hashed_password);
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION insert_employee(
    p_first_name VARCHAR(50),
    p_last_name VARCHAR(50),
    p_position VARCHAR(50),
    p_government_id INTEGER,
    p_employer_id INTEGER,
    p_created_by_user_id INTEGER
)
RETURNS text AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM employers WHERE id = p_employer_id) THEN
        RETURN 'Invalid employer_id: employee not inserted.';  
    END IF;
    INSERT INTO employees (first_name, last_name, position, government_id, employer_id, created_by_user_id)
    VALUES (p_first_name, p_last_name, p_position, p_government_id, p_employer_id, p_created_by_user_id);

    RETURN 'Employee created successfully.';  
END;
$$ LANGUAGE plpgsql;


-- Enable the pg_trgm extension for similarity calculations
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE OR REPLACE FUNCTION search_employees(
    search_term VARCHAR,
    page_num INTEGER,
    page_size INTEGER
)
RETURNS TABLE(
    id INTEGER,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    "position" VARCHAR(50),
    government_id INTEGER,
    employer_id INTEGER,
    created_by_user_id INTEGER,
    total_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    WITH search_results AS (
        SELECT * FROM employees AS e  
        WHERE e.first_name ILIKE '%' || search_term || '%'
           OR e.last_name ILIKE '%' || search_term || '%'
           OR e.position ILIKE '%' || search_term || '%'
           OR CAST(e.government_id AS text) ILIKE '%' || search_term || '%'
           OR CAST(e.employer_id AS text) ILIKE '%' || search_term || '%'
        ORDER BY GREATEST(
            similarity(e.first_name, search_term),
            similarity(e.last_name, search_term),
            similarity(e.position, search_term),
            similarity(CAST(e.government_id AS text), search_term),
            similarity(CAST(e.id AS text), search_term)
        ) DESC
        LIMIT page_size OFFSET (page_num - 1) * page_size
    )
    SELECT e.*, 
           (SELECT COUNT(*) FROM employees AS e2  
            WHERE e2.first_name ILIKE '%' || search_term || '%'
               OR e2.last_name ILIKE '%' || search_term || '%'
               OR e2.position ILIKE '%' || search_term || '%'
               OR CAST(e2.government_id AS text) ILIKE '%' || search_term || '%'
               OR CAST(e2.employer_id AS text) ILIKE '%' || search_term || '%') AS total_count
    FROM search_results AS e;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION insert_employer(
    p_employer_name VARCHAR(50),
    p_government_id INTEGER,
    p_created_by_user_id INTEGER
)
RETURNS void AS $$
BEGIN
    INSERT INTO employers (employer_name, government_id, created_by_user_id)
    VALUES (p_employer_name, p_government_id, p_created_by_user_id);
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION search_employers(
    search_term VARCHAR,
    page_num INTEGER,
    page_size INTEGER
)
RETURNS TABLE(
    id INTEGER,
    employer_name VARCHAR(50),
    government_id BIGINT,
    created_by_user_id INTEGER,
    total_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    WITH search_results AS (
        SELECT * FROM employers AS e 
        WHERE e.employer_name ILIKE '%' || search_term || '%'
           OR CAST(e.government_id AS text) ILIKE '%' || search_term || '%'
        ORDER BY GREATEST(
            similarity(e.employer_name, search_term),
            similarity(CAST(e.government_id AS text), search_term),
            similarity(CAST(e.id AS text), search_term)
        ) DESC
        LIMIT page_size OFFSET (page_num - 1) * page_size
    )
    SELECT e.*, 
           (SELECT COUNT(*) FROM employers AS e2  
            WHERE e2.employer_name ILIKE '%' || search_term || '%'
               OR CAST(e2.government_id AS text) ILIKE '%' || search_term || '%') AS total_count
    FROM search_results AS e;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION attach_employee_to_employer(
    p_employee_id INTEGER,
    p_employer_id INTEGER
)
RETURNS TEXT AS $$
DECLARE
    employee_exists BOOLEAN;
    employer_exists BOOLEAN;
BEGIN
    SELECT EXISTS(SELECT 1 FROM employees WHERE id = p_employee_id) INTO employee_exists;
    IF NOT employee_exists THEN
        RETURN 'Employee not found';
    END IF;
    SELECT EXISTS(SELECT 1 FROM employers WHERE id = p_employer_id) INTO employer_exists;
    IF NOT employer_exists THEN
        RETURN 'Employer not found';
    END IF;
    UPDATE employees SET employer_id = p_employer_id WHERE id = p_employee_id;
    RETURN 'Employee attached to employer successfully';
END;
$$ LANGUAGE plpgsql;