# scripts

this directory contains scripts and aws policies to be used within the apllication:

- `./scripts`:
  - `check_s3.py`: ensure aws connection and settings work as needed
  - `populate_db.py`: instantly populate the database

> [!NOTE]
>
> Due to their location, you'll have to run them as modules, e.g `python -m scripts.check_s3` from the root directory.

- `./scripts/policies`:
  - `aws_bucket_policy.json`:
  - `aws_iam_policy.json`:
