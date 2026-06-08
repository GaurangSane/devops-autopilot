# RUNBOOK TITLE:
Payment Service Connection Pool Exhaustion Runbook

# INCIDENT SUMMARY:
The payment-service experienced a connection pool exhaustion, leading to a cascade of failures including transaction rollbacks, circuit breaker openings, and ultimately a loss of database connection. This incident resulted in a complete loss of functionality for the payment-service, leading to failed orders and a compensation workflow being initiated.

# PREREQUISSES:
- Access to the payment-service configuration files
- Access to the NGINX configuration files
- Access to the database instance configuration
- Basic knowledge of Linux commands and scripting
- Familiarity with the payment-service architecture and dependencies

# DETECTION STEPS:
1. **Monitor payment-service logs**: Check the payment-service logs for connection pool exhaustion errors.
	* Expected outcome: Errors indicating connection pool exhaustion, such as "Connection pool exhausted" or "Timeout waiting for connection".
2. **Check database connection metrics**: Monitor database connection metrics, such as connection count and latency.
	* Expected outcome: High connection count and latency indicating a potential connection pool exhaustion issue.
3. **Verify circuit breaker status**: Check the circuit breaker status to see if it has opened due to repeated failures.
	* Expected outcome: Circuit breaker open, indicating that the payment-service is unavailable.

# DIAGNOSIS STEPS:
1. **Check payment-service configuration**: Verify the payment-service configuration, including the connection pool size and database connection settings.
	* Expected outcome: Configuration files indicating the current connection pool size and database connection settings.
2. **Analyze database queries**: Analyze database queries to identify potential performance bottlenecks.
	* Expected outcome: Identification of slow-running queries that may be contributing to the connection pool exhaustion issue.
3. **Check NGINX configuration**: Verify the NGINX configuration, including rate limiting and connection limiting settings.
	* Expected outcome: Configuration files indicating the current rate limiting and connection limiting settings.

# RESOLUTION STEPS:
1. **Increase connection pool size**: Increase the connection pool size to handle the increased load.
	* Command: `spring.datasource.hikari.maximum-pool-size=50`
	* Expected outcome: Connection pool size increased, allowing the payment-service to handle more connections.
2. **Implement rate limiting**: Configure NGINX to rate limit incoming requests to the payment-service.
	* Command: 
     ```
     limit_req_zone $binary_remote_addr zone=payment_service:10m rate=10r/s;
     server {
       location /payment-service/ {
         limit_req zone=payment_service;
         proxy_pass http://payment-service;
       }
     }
     ```
	* Expected outcome: Rate limiting enabled, preventing excessive requests to the payment-service.
3. **Optimize database queries**: Optimize database queries to reduce the load on the database.
	* Command: Use `EXPLAIN` statements to analyze query plans and optimize queries accordingly.
	* Expected outcome: Database queries optimized, reducing the load on the database.

# VERIFICATION STEPS:
1. **Verify payment-service availability**: Check the payment-service availability after implementing the fixes.
	* Expected outcome: Payment-service available, with no errors indicating connection pool exhaustion.
2. **Monitor database connection metrics**: Monitor database connection metrics to ensure the fixes have resolved the issue.
	* Expected outcome: Database connection metrics indicating a healthy connection pool, with no excessive latency or connection count.
3. **Verify circuit breaker status**: Check the circuit breaker status to ensure it has closed.
	* Expected outcome: Circuit breaker closed, indicating that the payment-service is available.

# ROLLBACK PLAN:
1. **Revert connection pool size**: Revert the connection pool size to its original value.
	* Command: `spring.datasource.hikari.maximum-pool-size=<original_value>`
	* Expected outcome: Connection pool size reverted, potentially causing the connection pool exhaustion issue to recur.
2. **Disable rate limiting**: Disable rate limiting in NGINX.
	* Command: Remove the `limit_req` directive from the NGINX configuration file.
	* Expected outcome: Rate limiting disabled, potentially allowing excessive requests to the payment-service.
3. **Revert database query optimizations**: Revert the database query optimizations.
	* Command: Revert the optimized queries to their original state.
	* Expected outcome: Database queries reverted, potentially causing performance issues.

# ESCALATION PATH:
1. **Notify on-call engineer**: Notify the on-call engineer if the issue persists after implementing the fixes.
2. **Escalate to senior engineer**: Escalate the issue to a senior engineer if the on-call engineer is unable to resolve the issue.
3. **Notify incident manager**: Notify the incident manager if the issue is critical and requires immediate attention.

# PREVENTION CHECKLIST:
1. **Regularly review payment-service configuration**: Regularly review the payment-service configuration to ensure it is optimized for the current load.
2. **Monitor database connection metrics**: Monitor database connection metrics to detect potential connection pool exhaustion issues.
3. **Implement automated testing**: Implement automated testing to detect potential issues before they occur.
4. **Regularly review and optimize database queries**: Regularly review and optimize database queries to reduce the load on the database.
5. **Implement load balancing and autoscaling**: Implement load balancing and autoscaling to handle increased traffic and reduce the load on the payment-service.