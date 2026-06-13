# RUNBOOK TITLE:
PostgreSQL Database Connection Failure Runbook

# INCIDENT SUMMARY:
The PostgreSQL database connection failed, causing the API to crash. The error occurred when trying to establish a connection to the database server at `127.0.0.1:5432`. This runbook provides step-by-step instructions to diagnose and resolve the issue.

# PREREQUISITES:
- Access to the server running the PostgreSQL database
- Sudo privileges to start and configure the PostgreSQL server
- Basic knowledge of Linux commands and PostgreSQL configuration

# DETECTION STEPS:
1. **Check API logs**: Look for error messages indicating a database connection failure.
2. **Verify PostgreSQL server status**: Run the command `sudo service postgresql status` to check if the PostgreSQL server is running.
3. **Check for error patterns**: Look for the error message "connection to server at '127.0.0.1', port 5432 failed: Connection refused (0x0000274D/10061)" in the API logs.

# DIAGNOSIS STEPS:
1. **Check PostgreSQL configuration**: Run the command `grep -H '^port' /etc/postgresql//main/postgresql.conf` to verify that PostgreSQL is configured to listen on the specified host and port.
2. **Verify firewall rules**: Check the firewall rules to ensure that incoming connections to the PostgreSQL port are allowed. Run the command `sudo ufw status` to verify the firewall rules.
3. **Check for network issues**: Verify that there are no network issues blocking the connection to the PostgreSQL server.

# RESOLUTION STEPS:
1. **Start PostgreSQL server**: If the server is not running, start it by running the command `sudo service postgresql start`.
2. **Edit PostgreSQL configuration**: If necessary, edit the `postgresql.conf` file to set the correct `listen_addresses` and `port`. Run the command `sudo nano /etc/postgresql/13/main/postgresql.conf` to edit the configuration file.
3. **Configure firewall rules**: Ensure that the firewall allows incoming connections to the PostgreSQL port. Run the command `sudo ufw allow postgresql` to configure the firewall rules.
4. **Restart PostgreSQL server**: After making any configuration changes, restart the PostgreSQL server by running the command `sudo service postgresql restart`.

# VERIFICATION STEPS:
1. **Verify PostgreSQL server status**: Run the command `sudo service postgresql status` to verify that the PostgreSQL server is running.
2. **Check API logs**: Verify that the API is able to connect to the database and that there are no error messages indicating a database connection failure.
3. **Test database connection**: Run a test query to verify that the database connection is working correctly.

# ROLLBACK PLAN:
If any of the resolution steps make the issue worse, follow these rollback steps:
1. **Revert PostgreSQL configuration changes**: Revert any changes made to the `postgresql.conf` file.
2. **Disable firewall rules**: Disable any firewall rules that were configured to allow incoming connections to the PostgreSQL port.
3. **Restart PostgreSQL server**: Restart the PostgreSQL server to ensure that any changes are reverted.

# ESCALATION PATH:
If the issue is not resolved after following the resolution steps, escalate the issue to a senior engineer or a database administrator. Provide detailed logs and error messages to aid in further diagnosis and resolution.

# PREVENTION CHECKLIST:
To prevent similar issues in the future, follow these steps:
1. **Regularly monitor PostgreSQL server status**: Set up monitoring to ensure the PostgreSQL server is running and accepting connections.
2. **Review and refine database configuration**: Regularly review and refine the database configuration to ensure optimal performance and security.
3. **Implement automated backup and recovery**: Set up automated backup and recovery processes to minimize data loss in case of a failure.
4. **Consider load balancing**: If the database server is experiencing high traffic, consider implementing load balancing to distribute the load.
5. **Schedule regular maintenance**: Schedule regular maintenance to ensure that the PostgreSQL server and database configuration are up-to-date and optimized.