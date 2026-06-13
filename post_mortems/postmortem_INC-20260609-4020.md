## INCIDENT TITLE:
`KeyError` Exception in `app.py` Script for "Failed Runs" Metric Display

## SEVERITY:
Medium

## DATE & DURATION:
The incident occurred on 2026-06-09 and lasted until the resolution was implemented. The exact duration is not specified, but the first sign of trouble occurred at 02:51:57.458.

## EXECUTIVE SUMMARY:
A medium-severity incident occurred on June 9, 2026, where the `app.py` script failed to display the "Failed Runs" metric due to a `KeyError` exception. This error was caused by the absence of the `'errors'` key in the `stats` dictionary. The incident did not cause a complete system failure but prevented the display of an important metric. The root cause is attributed to inadequate error handling and potential issues with the data collection or processing pipeline. Immediate and short-term fixes have been proposed to resolve the issue and prevent future occurrences.

## TIMELINE:
- 2026-06-09 02:51:57.458: The first sign of trouble occurred, indicating a `KeyError` exception in the `app.py` script.
- 2026-06-09 (time not specified): The incident was detected and diagnosed, revealing the absence of the `'errors'` key in the `stats` dictionary.
- 2026-06-09 (time not specified): Resolution steps were taken, including implementing the `.get()` method and adding try-except blocks to safely access the `'errors'` key.

## TECHNICAL SUMMARY:
The `app.py` script, which is part of the `devops-autopilot` application, relies on the `streamlit` framework to display metrics. The script attempted to access the `'errors'` key in the `stats` dictionary to display the "Failed Runs" metric but encountered a `KeyError` exception due to the key's absence. This error propagated through the `streamlit` framework, affecting the `devops-autopilot` application and its `ui` module.

## IMPACT ANALYSIS:
The incident impacted the display of the "Failed Runs" metric in the `ui` module of the `devops-autopilot` application. Although it did not cause a complete system failure, it prevented the display of an important metric that could be crucial for monitoring and debugging purposes. The impact is considered medium severity.

## ROOT CAUSE:
The primary root cause of the incident is the absence of the `'errors'` key in the `stats` dictionary when the `app.py` script attempts to display the "Failed Runs" metric. Contributing factors include inadequate error handling, potential issues with the data source or processing pipeline, and insufficient testing for scenarios where the `'errors'` key is missing.

## WHAT WENT WELL:
- The incident was contained within the metric display and did not cause a complete system failure, indicating some level of resilience within the system.
- The error was detected and diagnosed relatively quickly, allowing for prompt resolution.

## WHAT WENT WRONG:
- Inadequate error handling in the `app.py` script led to the `KeyError` exception.
- Potential issues with the data collection or processing pipeline may have resulted in the absence of the `'errors'` key in the `stats` dictionary.
- Insufficient testing for scenarios where the `'errors'` key is missing contributed to the incident.

## ACTION ITEMS:
| Task | Owner Role | Priority | Deadline |
| --- | --- | --- | --- |
| Implement the `.get()` method to safely access dictionary keys | Software Engineer | Immediate | 2026-06-10 |
| Add try-except blocks to catch and handle `KeyError` exceptions | Software Engineer | Immediate | 2026-06-10 |
| Validate input data to ensure expected keys are present | Software Engineer | Short-term | 2026-06-15 |
| Use a default dictionary to provide default values for missing keys | Software Engineer | Short-term | 2026-06-15 |
| Refactor the data collection or processing pipeline to ensure consistent data | Data Engineer | Long-term | 2026-07-01 |
| Implement robust error handling and logging mechanisms | Software Engineer | Long-term | 2026-07-01 |

## LESSONS LEARNED:
- The importance of adequate error handling in scripts that access dynamic data.
- The need for thorough testing of scenarios where data keys might be missing.
- The value of using safe methods to access dictionary keys, such as the `.get()` method.
- The potential for cascading failures when errors are not properly handled, emphasizing the need for robust error handling mechanisms.