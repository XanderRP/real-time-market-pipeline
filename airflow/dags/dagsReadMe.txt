Note to self – DAGS

This folder holds all the Airflow DAGs I’m writing to manage the data workflows.

Right now, this is where I’ll define things like:
- daily_summary_dag.py → aggregates daily prices + volumes by ticker
- any future ETL jobs I want to run on a schedule (e.g., exports, BigQuery uploads)

Airflow reads DAGs directly from this folder, so any Python file with a valid DAG object will automatically show up in the UI (http://localhost:8080).

Reminder:
- Use `@daily` or CRON expressions in `schedule_interval`
- Add `start_date` and `catchup=False` to avoid DAG backlogs during testing
- Logs are viewable in the Airflow UI

Future ideas:
- Add DAGs to export data to CSV/Parquet
- Add test DAGs that validate record counts or schema
