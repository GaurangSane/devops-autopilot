# RUNBOOK TITLE:
PostgreSQL Database Connection Issue Runbook

# INCIDENT SUMMARY:
The FastAPI application is unable to start due to a PostgreSQL database connection issue, resulting in a critical outage. The root cause is the PostgreSQL database server not running or not listening on the specified port (5432).

# PREREQUISITES:
* Access to the server hosting the PostgreSQL database
* Sudo privileges to start and configure the PostgreSQL server
* Knowledge of the PostgreSQL database configuration and settings

# DETECTION STEPS:
1. **Check application logs**: Look for error messages indicating a connection refused error (0x0000274D/10061) or Psycopg2 OperationalError.
2. **Verify PostgreSQL server status**: Run `netstat -nlp | grep 5432` or `ss -nlp | grep 5432` to check if the PostgreSQL server is listening on port 5432.
3. **Check PostgreSQL server process**: Run `pg_lsclusters` or `systemctl status postgresql` to verify if the PostgreSQL server is running.

# DIAGNOSIS STEPS:
1. **Check listen_addresses setting**: Run `grep listen_addresses /etc/postgresql/{version}/main/postgresql.conf` to ensure the `listen_addresses` setting is set to `'*'` or `''`.
2. **Verify database URL**: Check the database URL in the application configuration to ensure it is correct, including the host, port, username, password, and database name.
3. **Check firewall rules**: Run `ufw status` or `iptables -n -L` to verify if the firewall is blocking connections to the PostgreSQL server.

# RESOLUTION STEPS:
1. **Start PostgreSQL server**: Run `systemctl start postgresql` or `service postgresql start` to start the PostgreSQL server.
2. **Update listen_addresses setting**: Edit the `postgresql.conf` file using `nano /etc/postgresql/{version}/main/postgresql.conf` and set `listen_addresses` to `'*'` or `''`. Restart the server after updating the setting.
3. **Update pg_hba.conf**: Edit the `pg_hba.conf` file using `nano /etc/postgresql/{version}/main/pg_hba.conf` and add the line `host all all 0.0.0.0/0 trust` to allow connections from all IP addresses. Restart the server after updating the setting.
4. **Disable firewall**: Run `ufw disable` or `iptables -F` to temporarily disable the firewall and rule out firewall issues.

# VERIFICATION STEPS:
1. **Check application logs**: Verify that the application is starting up successfully and connecting to the PostgreSQL database.
2. **Run a test query**: Run a test query using `psql` or a database client to verify that the database connection is working.
3. **Check PostgreSQL server status**: Run `netstat -nlp | grep 5432` or `ss -nlp | grep 5432` to verify that the PostgreSQL server is listening on port 5432.

# ROLLBACK PLAN:
1. **Revert listen_addresses setting**: Edit the `postgresql.conf` file and revert the `listen_addresses` setting to its original value.
2. **Revert pg_hba.conf changes**: Edit the `pg_hba.conf` file and remove the added line `host all all 0.0.0.0/0 trust`.
3. **Re-enable firewall**: Run `ufw enable` or `iptables -F` to re-enable the firewall.

# ESCALATION PATH:
* **Primary contact**: Notify the primary contact (e.g., the database administrator) if the issue persists after following the resolution steps.
* **Secondary contact**: Notify the secondary contact (e.g., the application developer) if the primary contact is unavailable.
* **Escalation timeline**: Escalate the issue to the primary contact within 30 minutes, and to the secondary contact within 1 hour if the issue is not resolved.

# PREVENTION CHECKLIST:
1. **Regularly monitor PostgreSQL server status**: Set up monitoring tools like Prometheus and Grafana to track PostgreSQL server status and receive alerts for potential issues.
2. **Configure PostgreSQL for high availability**: Consider setting up a high-availability PostgreSQL cluster using tools like Patroni or Stolon to ensure database availability.
3. **Optimize database configuration**: Regularly review and optimize database configuration settings, such as `listen_addresses`, `max_connections`, and `shared_buffers`, to ensure optimal performance.
4. **Implement firewall rules**: Configure firewall rules to allow connections to the PostgreSQL server from authorized IP addresses.
5. **Test database connection regularly**: Regularly test the database connection to ensure it is working correctly.