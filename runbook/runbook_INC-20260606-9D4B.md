# RUNBOOK TITLE:
Payment Service Connection Pool Exhaustion Runbook

# INCIDENT SUMMARY:
The payment-service experienced a connection pool exhaustion, leading to a database connection loss, causing a cascade of failures, including transaction rollbacks, payment verification timeouts, and order failures. This runbook provides steps to diagnose and resolve the issue.

# PREREQUISITES:
- Access to the payment-service, api-gateway, order-service, load-balancer, and payments-db (postgresql database)
- Familiarity with PostgreSQL, pgbouncer, and NGINX configurations
- Ability to execute commands on the affected systems

# DETECTION STEPS:
1. **Check payment-service logs**: Look for connection pool exhaustion error messages in the payment-service logs.
	* Command: `sudo grep "connection pool exhaustion" /var/log/payment-service.log`
	* Expected outcome: Error messages indicating connection pool exhaustion.
2. **Verify database connection**: Check if the payment-service can establish a connection to the payments-db.
	* Command: `sudo -u postgres psql -c "SELECT 1;"`
	* Expected outcome: A successful connection to the database.
3. **Check load balancer status**: Verify the load balancer status to ensure the payment-service is not removed from the pool.
	* Command: `sudo curl http://load-balancer-ip:8080/healthcheck`
	* Expected outcome: A successful health check response.

# DIAGNOSIS STEPS:
1. **Analyze payment-service metrics**: Check metrics such as connection pool usage, database query latency, and error rates.
	* Command: `sudo curl http://payment-service-ip:8080/metrics`
	* Expected outcome: Metrics indicating high connection pool usage, increased query latency, and error rates.
2. **Check PostgreSQL configuration**: Verify the PostgreSQL configuration to ensure the max_connections setting is adequate.
	* Command: `sudo -u postgres psql -c "SHOW max_connections;"`
	* Expected outcome: The max_connections setting is adequate for the current load.
3. **Verify NGINX configuration**: Check the NGINX configuration to ensure rate limiting is enabled and configured correctly.
	* Command: `sudo nano /etc/nginx/nginx.conf`
	* Expected outcome: Rate limiting is enabled and configured correctly.

# RESOLUTION STEPS:
1. **Increase connection pool size**: Adjust the connection pool size to handle the increased traffic.
	* Command: `sudo nano /etc/pgbouncer/pgbouncer.ini`
	* Config Change:
		```
		[pgbouncer]
		default_pool_size = 50
		max_client_conn = 1000
		```
	* Expected outcome: The connection pool size is increased, and the payment-service can handle the increased traffic.
2. **Adjust PostgreSQL configuration**: Increase the max_connections setting in PostgreSQL to allow more connections.
	* Command: `sudo -u postgres psql -c "ALTER SYSTEM SET max_connections = 500;"`
	* Config Change: Edit `postgresql.conf` to persist the change after restart.
	* Expected outcome: The max_connections setting is increased, and the database can handle more connections.
3. **Implement rate limiting**: Use NGINX to limit the number of requests per second to prevent overwhelming the database.
	* Command: `sudo nano /etc/nginx/nginx.conf`
	* Config Change:
		```
		http {
			...
			limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
			...
			server {
				...
				location /api {
					limit_req zone=api_limit burst=20 nodelay;
					...
				}
			}
		}
		```
	* Expected outcome: Rate limiting is enabled, and the number of requests per second is limited.

# VERIFICATION STEPS:
1. **Verify payment-service status**: Check the payment-service status to ensure it is healthy and handling requests.
	* Command: `sudo curl http://payment-service-ip:8080/healthcheck`
	* Expected outcome: A successful health check response.
2. **Check database connection**: Verify the payment-service can establish a connection to the payments-db.
	* Command: `sudo -u postgres psql -c "SELECT 1;"`
	* Expected outcome: A successful connection to the database.
3. **Monitor metrics**: Monitor metrics such as connection pool usage, database query latency, and error rates to ensure the issue is resolved.
	* Command: `sudo curl http://payment-service-ip:8080/metrics`
	* Expected outcome: Metrics indicating normal connection pool usage, query latency, and error rates.

# ROLLBACK PLAN:
1. **Revert connection pool size**: Revert the connection pool size to its original value.
	* Command: `sudo nano /etc/pgbouncer/pgbouncer.ini`
	* Config Change:
		```
		[pgbouncer]
		default_pool_size = 20
		max_client_conn = 500
		```
	* Expected outcome: The connection pool size is reverted to its original value.
2. **Revert PostgreSQL configuration**: Revert the max_connections setting in PostgreSQL to its original value.
	* Command: `sudo -u postgres psql -c "ALTER SYSTEM SET max_connections = 200;"`
	* Config Change: Edit `postgresql.conf` to persist the change after restart.
	* Expected outcome: The max_connections setting is reverted to its original value.
3. **Disable rate limiting**: Disable rate limiting in NGINX.
	* Command: `sudo nano /etc/nginx/nginx.conf`
	* Config Change:
		```
		http {
			...
			# limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
			...
			server {
				...
				location /api {
					# limit_req zone=api_limit burst=20 nodelay;
					...
				}
			}
		}
		```
	* Expected outcome: Rate limiting is disabled.

# ESCALATION PATH:
1. **Notify team lead**: Notify the team lead of the issue and the steps taken to resolve it.
2. **Escalate to database team**: If the issue persists, escalate to the database team for further assistance.
3. **Escalate to infrastructure team**: If the issue is related to infrastructure, escalate to the infrastructure team for further assistance.

# PREVENTION CHECKLIST:
1. **Monitor connection pool usage**: Regularly monitor connection pool usage to detect potential issues.
2. **Monitor database query latency**: Regularly monitor database query latency to detect potential issues.
3. **Implement rate limiting**: Implement rate limiting to prevent overwhelming the database.
4. **Regularly review and optimize database queries**: Regularly review and optimize database queries to reduce the load on the database.
5. **Consider implementing a connection pooling library**: Consider implementing a connection pooling library to manage database connections efficiently.