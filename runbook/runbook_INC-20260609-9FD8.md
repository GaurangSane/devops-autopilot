# RUNBOOK TITLE:
Payment Service Connection Pool Exhaustion Runbook

# INCIDENT SUMMARY:
The payment-service experienced a connection pool exhaustion, leading to a failure in acquiring database connections, and ultimately resulting in a loss of database connection. This caused a cascade of failures in related services, including the api-gateway, order-service, and load-balancer.

# PREREQUISITES:
- Access to the payment-service configuration files
- Access to the PostgreSQL database configuration files
- Access to the load balancer configuration
- Basic knowledge of Linux command line and PostgreSQL

# DETECTION STEPS:
1. **Check payment-service logs**: Look for connection pool exhaustion errors in the payment-service logs.
	* Expected outcome: Errors indicating connection pool exhaustion, such as "Connection pool exhausted" or "Unable to acquire connection".
2. **Check PostgreSQL database logs**: Look for connection errors in the PostgreSQL database logs.
	* Expected outcome: Errors indicating connection issues, such as "Connection timeout" or "Connection refused".
3. **Check load balancer logs**: Look for errors indicating that the load balancer is unable to route traffic to the payment-service.
	* Expected outcome: Errors indicating that the load balancer is unable to connect to the payment-service, such as "Connection timeout" or "Connection refused".

# DIAGNOSIS STEPS:
1. **Check connection pool settings**: Verify that the connection pool settings are correctly configured.
	* Expected outcome: Connection pool settings are correctly configured, such as `pool_size = 100` and `connectionTimeoutMillis = 30000`.
2. **Check PostgreSQL database configuration**: Verify that the PostgreSQL database configuration is correctly set up.
	* Expected outcome: PostgreSQL database configuration is correctly set up, such as `max_connections = 500`.
3. **Check load balancer configuration**: Verify that the load balancer configuration is correctly set up.
	* Expected outcome: Load balancer configuration is correctly set up, such as health checks are enabled and configured correctly.

# RESOLUTION STEPS:
1. **Increase PostgreSQL max_connections**: Increase the `max_connections` setting in the PostgreSQL configuration file (`postgresql.conf`).
	* Command: `sudo nano /etc/postgresql/12/main/postgresql.conf` and update `max_connections = 500`.
	* Expected outcome: PostgreSQL database configuration is updated, and the `max_connections` setting is increased.
2. **Adjust connection pool settings**: Adjust the connection pool settings in the payment-service to prevent exhaustion.
	* Command: Update the connection pool settings in the payment-service configuration file, such as `pool_size = 100` and `connectionTimeoutMillis = 30000`.
	* Expected outcome: Connection pool settings are updated, and the payment-service is able to acquire connections successfully.
3. **Implement circuit breaker**: Implement a circuit breaker pattern in the payment-service to detect and prevent cascading failures.
	* Command: Update the payment-service code to implement a circuit breaker pattern, such as using Resilience4j.
	* Expected outcome: Circuit breaker pattern is implemented, and the payment-service is able to detect and prevent cascading failures.

# VERIFICATION STEPS:
1. **Check payment-service logs**: Verify that the payment-service logs no longer indicate connection pool exhaustion errors.
	* Expected outcome: Payment-service logs indicate that connections are being acquired successfully.
2. **Check PostgreSQL database logs**: Verify that the PostgreSQL database logs no longer indicate connection errors.
	* Expected outcome: PostgreSQL database logs indicate that connections are being established successfully.
3. **Check load balancer logs**: Verify that the load balancer logs no longer indicate errors routing traffic to the payment-service.
	* Expected outcome: Load balancer logs indicate that traffic is being routed successfully to the payment-service.

# ROLLBACK PLAN:
1. **Revert PostgreSQL max_connections**: Revert the `max_connections` setting in the PostgreSQL configuration file (`postgresql.conf`) to its original value.
	* Command: `sudo nano /etc/postgresql/12/main/postgresql.conf` and update `max_connections` to its original value.
	* Expected outcome: PostgreSQL database configuration is reverted, and the `max_connections` setting is restored to its original value.
2. **Revert connection pool settings**: Revert the connection pool settings in the payment-service to their original values.
	* Command: Update the connection pool settings in the payment-service configuration file to their original values.
	* Expected outcome: Connection pool settings are reverted, and the payment-service is restored to its original configuration.
3. **Revert circuit breaker implementation**: Revert the circuit breaker implementation in the payment-service to its original configuration.
	* Command: Update the payment-service code to revert the circuit breaker implementation.
	* Expected outcome: Circuit breaker implementation is reverted, and the payment-service is restored to its original configuration.

# ESCALATION PATH:
1. **Notify team lead**: Notify the team lead of the incident and the steps taken to resolve it.
2. **Notify engineering team**: Notify the engineering team of the incident and the steps taken to resolve it.
3. **Notify operations team**: Notify the operations team of the incident and the steps taken to resolve it.

# PREVENTION CHECKLIST:
1. **Monitor connection pool metrics**: Monitor connection pool metrics, such as utilization and wait times, to detect potential issues.
2. **Implement load balancer health checks**: Implement load balancer health checks to detect and prevent routing traffic to unhealthy instances.
3. **Optimize database queries**: Optimize database queries to reduce the load on the database and prevent connection pool exhaustion.
4. **Implement service discovery**: Implement service discovery to allow instances to register and deregister themselves with the load balancer.
5. **Implement autoscaling**: Implement autoscaling to allow the number of instances to scale up or down based on demand.
6. **Refactor architecture**: Refactor the architecture to reduce the load on the payment-service and prevent cascading failures.