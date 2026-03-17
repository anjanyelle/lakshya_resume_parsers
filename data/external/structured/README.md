# Structured Resume Datasets

This directory contains structured datasets for resume parsing and analysis.

## Dataset Files

### Core Datasets
- `skills.csv` - Technical and professional skills with categories
- `job_titles.csv` - Common job titles and positions
- `companies.csv` - Company names and identifiers
- `locations.csv` - Geographic locations (cities, states, countries)
- `education.csv` - Educational institutions and degrees
- `certifications.csv` - Professional certifications and credentials
- `clients.csv` - Client names and organizations

## File Format

All CSV files follow a consistent format:
- First row contains column headers
- UTF-8 encoding
- Comma-separated values
- No duplicate entries

## Usage

These datasets are used by:
- `NERExtractor` for named entity recognition
- `CompanyMatcher` for company name matching
- `LayoutSectionDetector` for section identification
- Other parser components for enhanced accuracy

## Maintenance

- Regular updates from industry sources
- Deduplication and validation processes
- Category tagging for better organization
