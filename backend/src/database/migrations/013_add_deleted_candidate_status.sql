-- Migration: Add 'deleted' value to candidate_status enum
-- Alter type statements cannot run inside transaction blocks in PG, so this SQL is executed outside transactions.

ALTER TYPE candidate_status ADD VALUE IF NOT EXISTS 'deleted';
