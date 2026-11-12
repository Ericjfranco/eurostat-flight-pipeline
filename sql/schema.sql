CREATE TABLE IF NOT EXISTS public.fact_air_traffic (
    dataset_code TEXT NOT NULL,
    period TEXT NOT NULL,
    geo_code TEXT NOT NULL DEFAULT 'UNKNOWN',
    geo_label TEXT,
    unit_code TEXT,
    unit_label TEXT,
    value DOUBLE PRECISION,
    dimensions JSONB NOT NULL DEFAULT '{}'::jsonb,
    dimension_labels JSONB NOT NULL DEFAULT '{}'::jsonb,
    source_updated TEXT,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (dataset_code, period, geo_code, dimensions)
);
CREATE INDEX IF NOT EXISTS idx_fact_air_traffic_period ON public.fact_air_traffic(period);
CREATE TABLE IF NOT EXISTS public.etl_execution_log (
    id BIGSERIAL PRIMARY KEY,
    dataset_code TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    status TEXT NOT NULL,
    records_extracted INTEGER DEFAULT 0,
    records_loaded INTEGER DEFAULT 0,
    message TEXT
);
