from airflow.operators.bash import BashOperator

spark_task = BashOperator(
    task_id='run_spark_summary',
    bash_command='spark-submit /opt/spark-apps/daily_summary_job.py',
    dag=dag,
)