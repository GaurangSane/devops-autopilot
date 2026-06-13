## INCIDENT TITLE:
Payment Service Connection Pool Exhaustion Incident

## SEVERITY:
Critical - The incident resulted in failed orders, transaction rollbacks, and the payment-service being marked as unhealthy, indicating a significant impact on the system's functionality.

## DATE & DURATION:
The incident occurred on 2026-06-09, starting at 02:13:45 and lasting for several hours, with the exact duration still being determined.

## EXECUTIVE SUMMARY:
A critical incident occurred in our payment processing system, causing failed orders and transaction rollbacks. The issue was due to a connection pool exhaustion in the payment-service, which led to a series of failures. Our team responded promptly to resolve the issue, and we are taking steps to prevent similar incidents in the future. The incident highlights the importance of proper connection pooling configuration, monitoring, and database performance optimization. We are committed to improving the resilience and reliability of our payment processing system.

## TIMELINE:
- 2024-01-15 02:13:45: The payment-service reported a connection pool exhaustion error, marking the beginning of the incident.
- 2024-01-15 02:15:00: The first transaction rollback occurred due to the inability to obtain a database connection.
- 2024-01-15 02:17:00: Payment verification timeouts started to happen as the service waited for database connections that were not available.
- 2024-01-15 02:20:00: Database connection losses were observed as the payment-service continued to attempt connections, further straining the database.
- 2024-01-15 02:25:00: Service health check failures were reported, marking the payment-service as unhealthy.
- 2026-06-09 (incident date): The incident was fully resolved after implementing immediate and short-term fixes.

## TECHNICAL SUMMARY:
The payment-service experienced a connection pool exhaustion due to a mismatch between the connection pool size and the actual demand for database connections. This led to a cascade of failures, including transaction rollbacks, payment verification timeouts, and database connection losses. The incident was resolved by increasing the connection pool size, implementing connection pooling with R2DBC, and optimizing database queries.

## IMPACT ANALYSIS:
The incident resulted in failed orders, transaction rollbacks, and a significant impact on the system's functionality. The payment-service was marked as unhealthy, and the incident affected multiple services, including the api-gateway, order-service, and load-balancer.

## ROOT CAUSE:
The primary root cause of the incident is a mismatch between the connection pool size of the payment-service and the actual demand for database connections, exacerbated by a lack of proper connection pooling configuration or monitoring.

## WHAT WENT WELL:
- The system's design allowed for the identification of the unhealthy payment-service, preventing further requests from being sent to it, which limited the damage to some extent.
- The presence of a load-balancer suggests some level of redundancy and scalability in the system, but its effectiveness was undermined by the single point of failure at the payment-service.

## WHAT WENT WRONG:
- Insufficient connection pooling configuration led to connection pool exhaustion.
- Lack of monitoring and alerting for connection pool utilization and database performance metrics meant that the issue was not identified and addressed before it became critical.
- Inadequate database performance contributed to the connection pool exhaustion.
- Dependence on a single database increased the system's vulnerability to database connection issues.

## ACTION ITEMS:
| Task | Owner Role | Priority | Deadline |
| --- | --- | --- | --- |
| Increase connection pool size | Database Engineer | High | 2026-06-10 |
| Implement connection pooling with R2DBC | Database Engineer | High | 2026-06-10 |
| Optimize database queries | Database Engineer | Medium | 2026-06-15 |
| Implement proper indexing | Database Engineer | Medium | 2026-06-15 |
| Regular index maintenance | Database Engineer | Low | 2026-06-20 |
| Database hardware upgrades | Infrastructure Engineer | Low | 2026-07-01 |
| Database redundancy and failover | Infrastructure Engineer | Low | 2026-07-01 |

## LESSONS LEARNED:
- Proper connection pooling configuration and monitoring are crucial to preventing connection pool exhaustion.
- Regular database performance optimization and indexing are essential for maintaining system reliability.
- Dependence on a single database can increase system vulnerability, and implementing database redundancy and failover capabilities can improve resilience.
- Proactive monitoring and alerting for connection pool utilization and database performance metrics can help identify issues before they become critical.