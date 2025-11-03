CREATE TABLE IF NOT EXISTS cache_records (
    Map VARCHAR(128) COLLATE utf8mb4_bin NOT NULL,
    Name VARCHAR(15) COLLATE utf8mb4_bin NOT NULL,
    Timestamp TIMESTAMP NOT NULL,
    Time FLOAT NOT NULL,
    PRIMARY KEY (Map, Name, Timestamp, Time)
);

START TRANSACTION;
DELETE FROM cache_records;
SET @best_so_far = NULL;
SET @prev_map = '';
INSERT INTO cache_records SELECT Map, Name, Timestamp, Time FROM (
    SELECT
        Map,
        Name,
        Timestamp,
        Time,
        @best_so_far := CASE
            WHEN @prev_map != Map THEN Time
            ELSE LEAST(@best_so_far, Time)
        END AS BestSoFar,
        @prev_map := Map
    FROM record_race WHERE Timestamp != 0 ORDER by Map, Timestamp
) t WHERE Time = BestSoFar;
COMMIT;
