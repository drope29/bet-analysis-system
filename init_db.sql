-- Create Enum for status
CREATE TYPE status_previsao AS ENUM ('pendente', 'green', 'red');

-- Create previsoes table
CREATE TABLE previsoes (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    time_casa VARCHAR(255) NOT NULL,
    time_fora VARCHAR(255) NOT NULL,
    dados_brutos JSONB,
    palpite_ia JSONB,
    resultado_real JSONB,
    status status_previsao DEFAULT 'pendente',
    licao_aprendida TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
