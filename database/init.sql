-- таблица пользователей.
CREATE TABLE IF NOT EXISTS users(
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE,
    username VARCHAR(100) UNIQUE,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- таблица запросов на анализ.
CREATE TABLE IF NOT EXISTS analysis_requests (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    source VARCHAR(20) NOT NULL CHECK (source IN('telegram','web')),
    input_text TEXT NOT NULL,
    ai_response_raw TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- таблица распарсенных резов.
CREATE TABLE IF NOT EXISTS parsed_results (
    id SERIAL PRIMARY KEY,
    request_id INTEGER REFERENCES analysis_requests(id) ON DELETE CASCADE,
    deficiency VARCHAR(100) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    recommended_food TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

-- Индексы для ускорения запросов
CREATE INDEX IF NOT EXISTS idx_analysis_requests_user_id ON analysis_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_analysis_requests_created_at ON analysis_requests(created_at);
CREATE INDEX IF NOT EXISTS idx_parsed_results_request_id ON parsed_results(request_id);