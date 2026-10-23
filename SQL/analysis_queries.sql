CREATE DATABASE IF NOT EXISTS banking_operations;
USE banking_operations;

SELECT 
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) AS successful_transactions,
    SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) AS failed_transactions,
    SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) AS pending_transactions,
    ROUND(100.0 * SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) AS success_rate_pct,
    ROUND(100.0 * SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) AS failure_rate_pct,
    ROUND(AVG(processing_time_sec), 2) AS avg_processing_time_sec
FROM transactions;

SELECT 
    channel,
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) AS successful_transactions,
    SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) AS failed_transactions,
    ROUND(100.0 * SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) AS failure_rate_pct,
    ROUND(AVG(processing_time_sec), 2) AS avg_processing_time_sec
FROM transactions
GROUP BY channel
ORDER BY failure_rate_pct DESC;

SELECT 
    transaction_date,
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) AS failed_transactions,
    ROUND(100.0 * SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) AS failure_rate_pct
FROM transactions
GROUP BY transaction_date
ORDER BY transaction_date;

SELECT 
    DATE_FORMAT(transaction_date, '%Y-%m-01') AS month,
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) AS successful_transactions,
    SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) AS failed_transactions
FROM transactions
GROUP BY DATE_FORMAT(transaction_date, '%Y-%m-01')
ORDER BY month;

SELECT 
    failure_reason,
    COUNT(*) AS failed_transactions,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM transactions WHERE status = 'Failed'), 2) AS share_of_failures_pct
FROM transactions
WHERE status = 'Failed'
GROUP BY failure_reason
ORDER BY failed_transactions DESC;

SELECT 
    region,
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) AS failed_transactions,
    ROUND(100.0 * SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) AS failure_rate_pct,
    SUM(complaint_flag) AS complaints,
    ROUND(AVG(processing_time_sec), 2) AS avg_processing_time_sec
FROM transactions
GROUP BY region
ORDER BY failure_rate_pct DESC;

SELECT 
    status,
    COUNT(*) AS total_transactions,
    SUM(complaint_flag) AS complaints,
    ROUND(100.0 * SUM(complaint_flag) / NULLIF(COUNT(*), 0), 2) AS complaint_rate_pct
FROM transactions
GROUP BY status
ORDER BY complaint_rate_pct DESC;

SELECT 
    transaction_type,
    COUNT(*) AS total_transactions,
    ROUND(AVG(amount_inr), 2) AS avg_amount_inr
FROM transactions
GROUP BY transaction_type
ORDER BY total_transactions DESC;

WITH channel_metrics AS (
    SELECT 
        channel,
        COUNT(*) AS total_transactions,
        SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) AS failed_transactions
    FROM transactions
    GROUP BY channel
)
SELECT 
    channel, 
    total_transactions, 
    failed_transactions,
    ROUND(100.0 * failed_transactions / NULLIF(total_transactions, 0), 2) AS failure_rate_pct,
    DENSE_RANK() OVER (
        ORDER BY (failed_transactions / NULLIF(total_transactions, 0)) DESC
    ) AS failure_rate_rank
FROM channel_metrics;

SELECT
    COUNT(*) AS row_count,
    COUNT(DISTINCT transaction_id) AS distinct_transaction_ids,
    SUM(CASE WHEN transaction_id IS NULL THEN 1 ELSE 0 END) AS missing_transaction_ids,
    SUM(CASE WHEN amount_inr < 0 THEN 1 ELSE 0 END) AS negative_amounts,
    SUM(CASE WHEN processing_time_sec < 0 THEN 1 ELSE 0 END) AS negative_processing_times
FROM transactions;
