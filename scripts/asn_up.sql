CREATE TABLE IF NOT EXISTS asn_info (
    asn_number INTEGER PRIMARY KEY,
    start_ip TEXT,
    end_ip TEXT,
    country_code TEXT,
    registered_to TEXT
);
