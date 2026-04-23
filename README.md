# SQL-Faker: Database-Native Synthetic Data Generation

This project provides a set of PostgreSQL stored procedures designed to generate synthetic user data deterministically. By performing data generation directly inside the database, we achieve high-performance throughput (~2000+ users/sec) and avoid the latency of transferring large datasets from an application server.

## Architecture & Design Principles

The primary design principle is **determinism**. Every function accepts a `seed` argument. Given the same `seed` and `locale`, the database will always produce the exact same result. This makes testing, debugging, and reproducibility straightforward.

### Key Algorithms
- **Deterministic Randomness:** We utilize `md5(concat(column_name, p_seed))` to generate a consistent pseudo-random bit string based on the input seed.
- **Categorical Data:** Uses hash-based modulo arithmetic to select items from a `lookup_data` table, ensuring an even distribution.
- **Normal Distribution (Box-Muller Transform):** To generate realistic human attributes like height and weight, we use the Box-Muller transform:
  - $Z = \sqrt{-2 \ln(U_1)} \cdot \cos(2\pi U_2)$
  - Result = $(Z \cdot \sigma) + \mu$
- **Geo-Data Generation:** Uses uniform probability density functions (PDF). Latitude is processed via `asin` to ensure uniform distribution across the spherical surface of the Earth, preventing clustering at the poles.

---

## Stored Procedures Documentation

### `generate_user(p_seed INT, p_locale TEXT)`
The main entry point. Orchestrates all helper functions to create a full user record.
- **Arguments:**
  - `p_seed` (INT): Seed for deterministic output.
  - `p_locale` (TEXT): Cultural context (e.g., 'de', 'en').
- **Returns:** A table row with `first_name`, `last_name`, `city`, `lat`, `lon`, `height`, `weight`.

### `get_random_value(p_seed INT, p_locale TEXT, p_category TEXT)`
Fetches categorical data from the lookup table.
- **Logic:** Calculates record count, generates a hash offset, and performs `LIMIT 1 OFFSET offset`.

### `get_random_normal(p_seed INT, p_mean NUMERIC, p_stddev NUMERIC)`
Generates normally distributed numeric data.
- **Usage:** Perfect for generating physical attributes.
- **Example:** `SELECT get_random_normal(101, 175, 7); -- Generates height`

### `get_random_lat(p_seed INT)` / `get_random_lon(p_seed INT)`
Generates coordinates. 
- **Latitude:** Uniformly distributed using arccosine/arcsine logic for spherical mapping.
- **Longitude:** Uniformly distributed across [-180, 180].

---

## Usage Example

To generate a user directly via SQL:

```sql
-- Generate a single deterministic user
SELECT * FROM generate_user(101, 'de');
