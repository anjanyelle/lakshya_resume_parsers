-- Migration: Add 'duplicate' and 'merged' values to review_status enum
-- Alter type statements cannot run inside transaction blocks in PG, so this SQL is executed outside transactions.

ALTER TYPE review_status ADD VALUE IF NOT EXISTS 'duplicate';
ALTER TYPE review_status ADD VALUE IF NOT EXISTS 'merged';
