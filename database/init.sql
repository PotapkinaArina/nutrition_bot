-- таблица пользователей.
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname='nutrition_user') THEN
        CREATE ROLE nutrition_user WITH LOGIN PASSWORD 'OchPlohoyParol';
    END IF;
END
$$;

SELECT 'CREATE DATABASE nutrition_db OWNER nutrition_user'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname='nutrition_db')\gexec


CREATE TABLE IF NOT EXISTS users(
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE,
    username VARCHAR(100) UNIQUE,
    email VARCHAR(255) UNIQUE,
    weight DECIMAL(5,2),
    height DECIMAL(5,2),
    age INTEGER,
    gender VARCHAR(10),
    activity_level VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- таблица запросов на анализ.
CREATE TABLE IF NOT EXISTS analysis_requests (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    source VARCHAR(20) NOT NULL CHECK (source IN('telegram','web')),
    input_text TEXT NOT NULL,
    ai_response_raw TEXT,
    calories INTEGER,
    protein DECIMAL(5,2), --белки в граммах г.
    fat DECIMAL(5,2), --жиры в граммах.
    carbs DECIMAL(5,2), --УГЛЕВОДЫ г.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- таблица распарсенных резов. дефициты для лохов и чайников. ыгыывых
CREATE TABLE IF NOT EXISTS parsed_results (
    id SERIAL PRIMARY KEY,
    request_id INTEGER REFERENCES analysis_requests(id) ON DELETE CASCADE,
    deficiency VARCHAR(100) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    recommended_food TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS weight_history (

    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    weight DECIMAL(5,2) NOT NULL,
    bmi DECIMAL(4,2),
    body_fat DECIMAL(4,2),
    muscle_mass DECIMAL(5,2),
    measurement_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);




-- Индексы для ускорения запросов
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_weight_history_user_id ON weight_history(user_id);
CREATE INDEX IF NOT EXISTS idx_weight_history_date ON weight_history(measurement_date);
CREATE INDEX IF NOT EXISTS idx_analysis_requests_user_id ON analysis_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_analysis_requests_created_at ON analysis_requests(created_at);
CREATE INDEX IF NOT EXISTS idx_parsed_results_request_id ON parsed_results(request_id);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


--INSERT INTO users (telegram_id, username,weight,height,age,gender)
--VALUES
  --  (123456789, 'test_user', 65.4, 168.9, 25, 'female'),
   -- (987654321, 'demo_user', 70.5, 172.0, 20, 'male')
--ON CONFLICT (telegram_id) DO NOTHING;