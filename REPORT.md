# RepairLink: A RESTful Maintenance Reporting and Tracking System for Off-Campus Students

**Module:** NADV 744 – Advanced Development Systems  
**Assessment:** Group Assignment 2026  
**Project:** RepairLink  
**Status:** Working report draft for group completion  
**Repository:** `ThabangMmusi/RepairLink`

> Replace the placeholders for student names, student numbers, screenshots, measured results, and final Git commit information before submission.

## 1. Problem definition

Off-campus students and campus users regularly encounter maintenance problems such as broken lights, plumbing failures, damaged furniture, internet faults, unsafe walkways, and security-related defects. When these problems are reported through informal messages or separate channels, reports can be lost, duplicated, or difficult to follow up. A student may not know whether a problem has been received, whether maintenance work has started, or whether a reported problem was actually resolved.

RepairLink addresses this problem through a single-user RESTful service. The primary user is the student who submits and tracks a maintenance report. The system captures the location, category, description, urgency, safety risk, and number of affected people. It returns a unique reference number and maintains a status history from submission to resolution. The student can also reopen a report when the problem has not been properly resolved and submit feedback after resolution.

The project is relevant to information and communication technology because it applies service-oriented design, API communication, structured data validation, workflow rules, persistence, error handling, and automated testing to a realistic institutional problem.

### Objectives

The project objectives are to provide a clear maintenance-reporting workflow, prevent duplicate reports, calculate transparent priorities, preserve report history, expose a documented REST API, and evaluate the system through automated tests and basic performance measurements.

### Planned resources

The project uses Python 3.11+, FastAPI, SQLAlchemy, SQLite, Pytest, Git, GitHub, cURL, and the automatically generated OpenAPI documentation. The project is designed to run in a local Python virtual environment named `.venv`, which isolates its dependencies from the host installation.

## 2. System design

### Architecture

```text
+---------------------------+
| Student / API Client      |
| Swagger, cURL or frontend |
+-------------+-------------+
              |
              v
+---------------------------+
| FastAPI REST API          |
| Routing and HTTP errors   |
+-------------+-------------+
              |
              v
+---------------------------+
| Validation and services   |
| Priority calculation      |
| Duplicate detection       |
| Status transition rules   |
+-------------+-------------+
              |
              v
+---------------------------+
| SQLAlchemy data layer     |
| ORM models and sessions   |
+-------------+-------------+
              |
              v
+---------------------------+
| SQLite database           |
| Reports, updates, feedback|
+---------------------------+
```

The student interacts with the API through Swagger UI, cURL, Postman, or a future web interface. FastAPI validates incoming JSON and routes requests. The service layer applies the priority, duplicate-detection, and status-transition rules. SQLAlchemy persists the report, status-history, and feedback records in SQLite.

### Data model

| Entity | Main fields | Purpose |
|---|---|---|
| MaintenanceReport | Reference, location, category, description, urgency, priority, status, timestamps | Stores the main maintenance problem |
| ReportUpdate | Previous status, new status, note, timestamp | Preserves the report workflow history |
| Feedback | Rating, comment, timestamp | Stores student feedback after resolution |

### REST endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Confirms that the service is running |
| `POST` | `/api/reports` | Creates a maintenance report |
| `GET` | `/api/reports` | Lists reports, with optional status filtering |
| `GET` | `/api/reports/{id}` | Retrieves one report with history and feedback |
| `PATCH` | `/api/reports/{id}/status` | Applies a valid workflow transition |
| `POST` | `/api/reports/{id}/reopen` | Reopens a resolved report |
| `POST` | `/api/reports/{id}/feedback` | Adds a rating and comment after resolution |
| `GET` | `/api/reports/dashboard/summary` | Returns report and feedback statistics |
| `GET` | `/api/locations` | Returns supported campus and residence locations |
| `GET` | `/api/categories` | Returns categories and urgency values |

### Status workflow

```text
SUBMITTED → RECEIVED → ASSIGNED → IN_PROGRESS → RESOLVED
                                      ^              |
                                      |              v
                                      +---------- REOPENED
```

Only documented transitions are accepted. For example, a report cannot move directly from `SUBMITTED` to `RESOLVED`. This prevents inconsistent records and demonstrates domain-level business logic.

### Security and privacy approach

The assignment prototype uses one primary student user and does not collect real sensitive information. The system should be extended with authentication and role-based access control before production use. The development database is local, `.env` is excluded from Git, and the test suite uses an in-memory database. Student names, contact information, and photographs should be fictional or omitted during the demonstration.

## 3. Implementation

The backend is organized into configuration, database, models, schemas, routers, and services. Pydantic schemas validate request fields before they reach the business layer. SQLAlchemy models provide database persistence without embedding raw SQL in endpoint handlers.

The priority calculation uses a transparent rule. The urgency contributes between one and four points. A safety risk contributes three points, and a problem affecting multiple people contributes two points. The final score is mapped to `normal`, `high`, or `critical`.

Duplicate detection searches for an unresolved report with the same location and category submitted during the previous 24 hours. If one exists, the API returns HTTP `409 Conflict` with the existing reference number instead of creating an unnecessary duplicate.

The API also returns structured errors. Examples include `REPORT_NOT_FOUND`, `DUPLICATE_REPORT`, `INVALID_STATUS_TRANSITION`, `REPORT_NOT_RESOLVED`, and `FEEDBACK_EXISTS`. These codes make errors easier for clients to interpret and easier to demonstrate during the presentation.

## 4. Testing and evaluation

### Test plan

| Test area | Test case | Expected result |
|---|---|---|
| Health | Request `/health` | HTTP 200 and `status=ok` |
| Creation | Submit a valid report | HTTP 201 and generated reference |
| Validation | Submit a description shorter than 20 characters | HTTP 422 |
| Duplicate detection | Submit the same open problem twice | HTTP 409 and duplicate code |
| Priority | Submit a critical safety-related problem | Critical priority label |
| Workflow | Move through valid states | Each transition succeeds |
| Workflow | Move directly from submitted to resolved | HTTP 422 and transition error |
| Missing data | Request a nonexistent report | HTTP 404 and report-not-found code |
| Resolution | Add feedback before resolution | HTTP 422 |
| Feedback | Add feedback after resolution | HTTP 201 |
| Reopening | Reopen a resolved report | Status becomes reopened |
| Dashboard | Create and resolve a report | Counts reflect the current state |

The repository contains automated Pytest tests for these cases. The tests use an in-memory SQLite database so that test data does not alter the local development database.

### Performance evaluation plan

Before final submission, run the service locally and record at least three measurements: report creation response time, report-list response time, and dashboard response time. Repeat each request at least 20 times and report the average and maximum values. The group should also test the list endpoint with increasing data volumes, such as 50, 500, and 1,000 records, while documenting the machine specifications and test method.

The final report should add a small table similar to the following after measurements are completed:

| Endpoint | Number of requests | Average response time | Maximum response time |
|---|---:|---:|---:|
| `POST /api/reports` | To be measured | To be measured | To be measured |
| `GET /api/reports` | To be measured | To be measured | To be measured |
| `GET /api/reports/dashboard/summary` | To be measured | To be measured | To be measured |

These measurements are local prototype results, not a claim about production capacity. A production deployment would require a production database, authentication, monitoring, rate limiting, and load testing in a controlled environment.

## 5. Results and discussion

The current implementation provides a complete core workflow: a student can submit a report, receive a reference, view its status, progress it through the maintenance workflow, record resolution, reopen it, and provide feedback. The duplicate rule and status-transition rule demonstrate that RepairLink contains business logic beyond simple database creation and retrieval.

The generated Swagger documentation makes the API easy to explore during the demonstration. The structured error responses make invalid inputs visible and provide evidence for the error-handling requirement. The test suite provides repeatable evidence that normal and negative scenarios were considered.

For the final submission, insert screenshots of the Swagger interface, a successful report response, a duplicate-report error, a status-history response, and the dashboard summary. The group should also include the final test output and performance table.

## 6. Limitations

RepairLink is an academic prototype. It does not currently include a production authentication system, real maintenance-department accounts, real-time push notifications, image storage, map integration, or a deployed cloud database. The maintenance updates are entered through the API for demonstration purposes because the project intentionally has one primary human user.

The duplicate-detection rule uses exact location and category matching. It may not detect two reports that describe the same problem with different wording or slightly different locations. Priority scoring is intentionally transparent and rule-based; it is not a professional emergency-response classification system.

## 7. Future improvements

Future versions could add student authentication, maintenance-staff roles, email or mobile notifications, image uploads, map-based location selection, maintenance-team assignment, richer analytics, full-text similarity for duplicate detection, and PostgreSQL deployment. These features should be added only after the core workflow has been tested and secured.

## 8. Demonstration script

The five-minute demonstration should begin at `/docs`. First, create a high-priority electrical report at an off-campus residence. Second, submit a duplicate report to demonstrate the `409 Conflict` response. Third, move the original report through `received`, `assigned`, `in_progress`, and `resolved`. Fourth, retrieve the report and show its history. Fifth, submit feedback and display the dashboard summary. Finally, reopen the report to show how an unresolved repair is handled.

## 9. Conclusion

RepairLink demonstrates how a focused service-driven system can address a practical student problem without unnecessary complexity. The system uses a clear REST API, modular Python code, validation, persistence, workflow rules, structured errors, automated tests, and reproducible setup instructions. Its single-user scope makes it feasible to complete while leaving enough technical depth to satisfy the NADV744 requirements.

## References

[1]: https://fastapi.tiangolo.com/ "FastAPI Documentation"

[2]: https://docs.sqlalchemy.org/en/20/orm/quickstart.html "SQLAlchemy ORM Quick Start"

[3]: https://docs.pytest.org/en/stable/ "pytest Documentation"
