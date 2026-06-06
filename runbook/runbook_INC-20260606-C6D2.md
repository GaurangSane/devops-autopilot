# RUNBOOK TITLE:
Payment Service Connection Pool Exhaustion Runbook

# INCIDENT SUMMARY:
The payment-service experienced a connection pool exhaustion, leading to a database connection loss, causing a cascade of failures, including transaction rollbacks, payment verification timeouts, and order failures. This runbook provides steps to diagnose and resolve the issue.

# PREREQUISITES:
- Access to the payment-service configuration files (e.g., `application.yml`)
- Access to the PostgreSQL database configuration files
- Access to the NGINX configuration files
- Basic knowledge of PostgreSQL, NGINX, and the payment-service architecture

# DETECTION STEPS:
1. **Monitor payment-service logs**: Check the payment-service logs for connection pool exhaustion errors.
	* Expected outcome: Identify the error message indicating connection pool exhaustion.
2. **Check database connection status**: Verify the database connection status using PostgreSQL tools (e.g., `pg_stat_activity`).
	* Expected outcome: Confirm the database connection loss.
3. **Verify service unavailability**: Check the api-gateway and load-balancer logs for service unavailability errors.
	* Expected outcome: Identify the error messages indicating service unavailability.

# DIAGNOSIS STEPS:
1. **Check connection pool configuration**: Verify the connection pool configuration in the `application.yml` file.
	* Expected outcome: Identify the current connection pool size.
2. **Analyze database query performance**: Use PostgreSQL's built-in tools (e.g., `EXPLAIN` and `EXPLAIN ANALYZE`) to analyze query performance.
	* Expected outcome: Identify slow queries consuming connections.
3. **Check PostgreSQL buffer pool size**: Verify the PostgreSQL buffer pool size in the PostgreSQL configuration file.
	* Expected outcome: Identify the current buffer pool size.

# RESOLUTION STEPS:
1. **Increase connection pool size**:
	* Edit the `application.yml` file: `spring.datasource.hikari.maximum-pool-size: 30`
	* Restart the payment-service
	* Expected outcome: Increased connection pool size to handle the increased load
2. **Implement rate limiting**:
	* Edit the NGINX configuration file: 
	```
	limit_req_zone $binary_remote_addr zone=one:10m rate=5r/s;
	server {
	  location / {
	    limit_req zone=one burst=10 nodelay;
	  }
	}
	```
	* Restart NGINX
	* Expected outcome: Rate limiting implemented to prevent overwhelming the payment-service
3. **Optimize database queries**:
	* Identify and optimize slow queries using PostgreSQL's built-in tools
	* Expected outcome: Improved query performance and reduced connection consumption

# VERIFICATION STEPS:
1. **Verify connection pool size**: Check the payment-service logs to confirm the increased connection pool size.
	* Expected outcome: Confirm the updated connection pool size.
2. **Verify rate limiting**: Test the rate limiting configuration using tools like `curl` or `ab`.
	* Expected outcome: Confirm the rate limiting is working as expected.
3. **Verify database query performance**: Monitor the database query performance using PostgreSQL's built-in tools.
	* Expected outcome: Confirm the improved query performance.

# ROLLBACK PLAN:
1. **Revert connection pool size**: Edit the `application.yml` file to revert the connection pool size to its original value.
2. **Remove rate limiting**: Edit the NGINX configuration file to remove the rate limiting configuration.
3. **Revert database query optimizations**: Revert any database query optimizations made during the resolution steps.

# ESCALATION PATH:
1. **Notify the on-call engineer**: If the issue persists after following the resolution steps, notify the on-call engineer.
2. **Escalate to the database team**: If the issue is related to the PostgreSQL database, escalate to the database team.
3. **Escalate to the infrastructure team**: If the issue is related to the infrastructure, escalate to the infrastructure team.

# PREVENTION CHECKLIST:
1. **Regularly review connection pool configuration**: Verify the connection pool size is adequate for the expected load.
2. **Monitor database query performance**: Regularly monitor database query performance to identify and optimize slow queries.
3. **Implement load testing**: Regularly perform load testing to identify and mitigate bottlenecks.
4. **Implement traffic management**: Implement mechanisms to manage sudden spikes in traffic, such as rate limiting or queueing.
5. **Regularly review and update the runbook**: Review and update the runbook to ensure it remains relevant and effective.