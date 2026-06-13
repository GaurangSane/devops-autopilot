# RUNBOOK TITLE:
Payment-Service Connection Pool Exhaustion Runbook

# INCIDENT SUMMARY:
The payment-service experienced a connection pool exhaustion, leading to a cascade of failures including transaction rollbacks, circuit breaker openings, and ultimately a loss of database connection. This incident resulted in a complete loss of functionality for the payment-service, leading to failed orders and a compensation workflow being initiated.

# PREREQUISITES:
- Access to the payment-service and PostgreSQL database
- Knowledge of PgBouncer and PostgreSQL configuration
- Ability to execute commands on the payment-service and database servers
- Familiarity with Kubernetes (for short-term fixes)

# DETECTION STEPS:
1. **Monitor payment-service logs**: Check the payment-service logs for connection pool exhaustion errors.
	* Expected outcome: Identify the error message indicating connection pool exhaustion.
2. **Check database connection status**: Verify the database connection status using `pg_stat_activity` or similar commands.
	* Expected outcome: Confirm the loss of database connections.
3. **Verify circuit breaker status**: Check the circuit breaker status to ensure it is open.
	* Expected outcome: Confirm the circuit breaker is open.

# DIAGNOSIS STEPS:
1. **Analyze payment-service metrics**: Review payment-service metrics (e.g., CPU utilization, memory usage) to identify potential causes of the connection pool exhaustion.
	* Expected outcome: Identify potential causes of the connection pool exhaustion.
2. **Check PostgreSQL configuration**: Verify the PostgreSQL configuration to ensure it is optimized for connection handling and performance.
	* Expected outcome: Identify potential configuration issues.
3. **Investigate recent changes**: Investigate recent changes to the payment-service or database configuration that may have contributed to the incident.
	* Expected outcome: Identify potential contributing factors.

# RESOLUTION STEPS:
## Immediate Fixes
1. **Implement PgBouncer**: Implement PgBouncer to prevent connection pool exhaustion.
	* Command: `pgbouncer -d /etc/pgbouncer/pgbouncer.ini`
	* Config (`pgbouncer.ini`):
		```
		[databases]
		mydb = host=localhost port=5432 dbname=mydb

		[pgbouncer]
		listen_addr = 0.0.0.0
		listen_port = 6432
		auth_type = md5
		auth_file = /etc/pgbouncer/userlist.txt
		pool_mode = transaction
		default_pool_size = 20
		min_pool_size = 5
		reserve_pool_size = 5
		reserve_pool_timeout = 3
		server_connect_timeout = 15
		server_idle_timeout = 600
		```
	* Expected outcome: Connection pool exhaustion errors should decrease.
2. **Adjust PostgreSQL configuration**: Adjust the PostgreSQL configuration to optimize connection handling and performance.
	* Command: `sudo nano /etc/postgresql/13/main/postgresql.conf` (adjust the file path according to your PostgreSQL version)
	* Config (`postgresql.conf`):
		```
		max_connections = 100
		shared_buffers = 512MB
		work_mem = 4MB
		```
	* Expected outcome: Database performance should improve.

## Short-term Fixes
1. **Implement Horizontal Pod Autoscaling (HPA)**: Implement HPA to scale the payment-service deployment based on CPU utilization.
	* Command: `kubectl apply -f hpa.yaml`
	* Config (`hpa.yaml`):
		```
		apiVersion: autoscaling/v2
		kind: HorizontalPodAutoscaler
		metadata:
		  name: payment-service-hpa
		spec:
		  selector:
		    matchLabels:
		      app: payment-service
		  minReplicas: 1
		  maxReplicas: 10
		  metrics:
		  - type: Resource
		    resource:
		      name: cpu
		      target:
		        type: Utilization
		        averageUtilization: 50
		```
	* Expected outcome: Payment-service deployment should scale according to CPU utilization.
2. **Implement Circuit Breaker Pattern**: Implement the circuit breaker pattern using Resilience4J to prevent cascading failures.
	* Command: `mvn clean install` (after adding Resilience4J dependency)
	* Config (`application.yml`):
		```
		resilience4j:
		  circuitbreaker:
		    instances:
		      paymentService:
		        registerHealthIndicator: true
		        slidingWindowSize: 10
		        minimumNumberOfCalls: 5
		        failureRateThreshold: 50
		        waitDurationInOpenState: 10s
		```
	* Expected outcome: Circuit breaker should prevent cascading failures.

# VERIFICATION STEPS:
1. **Monitor payment-service logs**: Verify that connection pool exhaustion errors have decreased.
	* Expected outcome: Connection pool exhaustion errors should be minimal or non-existent.
2. **Check database connection status**: Verify that database connections are stable.
	* Expected outcome: Database connections should be stable.
3. **Verify circuit breaker status**: Verify that the circuit breaker is closed.
	* Expected outcome: Circuit breaker should be closed.

# ROLLBACK PLAN:
1. **Revert PgBouncer configuration**: Revert the PgBouncer configuration to its previous state.
	* Command: `pgbouncer -d /etc/pgbouncer/pgbouncer.ini` (with previous configuration)
2. **Revert PostgreSQL configuration**: Revert the PostgreSQL configuration to its previous state.
	* Command: `sudo nano /etc/postgresql/13/main/postgresql.conf` (with previous configuration)
3. **Revert HPA configuration**: Revert the HPA configuration to its previous state.
	* Command: `kubectl delete -f hpa.yaml`
4. **Revert Circuit Breaker configuration**: Revert the Circuit Breaker configuration to its previous state.
	* Command: `mvn clean install` (with previous configuration)

# ESCALATION PATH:
1. **Notify on-call engineer**: Notify the on-call engineer if the issue persists after attempting the resolution steps.
2. **Escalate to senior engineer**: Escalate the issue to a senior engineer if the on-call engineer is unable to resolve the issue.
3. **Invoke incident response plan**: Invoke the incident response plan if the issue has a significant impact on the business.

# PREVENTION CHECKLIST:
1. **Regularly review payment-service metrics**: Regularly review payment-service metrics to identify potential issues.
2. **Monitor database connection status**: Monitor database connection status to identify potential issues.
3. **Implement automated testing**: Implement automated testing to identify potential issues before they occur.
4. **Regularly review and update configuration**: Regularly review and update configuration to ensure it is optimized for performance and security.
5. **Implement continuous monitoring and logging**: Implement continuous monitoring and logging to identify potential issues and improve incident response.