# GitHub Copilot Instructions for Mergington High School API

## Project Overview
This is a High School Management System API built with FastAPI. The application allows students to view and sign up for extracurricular activities at Mergington High School.

## Tech Stack
- **Framework**: FastAPI
- **Language**: Python 3
- **Testing**: pytest with TestClient
- **HTTP Client**: httpx (for testing)
- **Server**: uvicorn

## Project Structure
```
/home/runner/work/Mona/Mona/
├── src/
│   ├── app.py           # Main FastAPI application
│   └── static/          # Static web files
├── tests/
│   └── test_app.py      # API tests
├── requirements.txt      # Python dependencies
└── pytest.ini           # Test configuration
```

## Code Style and Conventions

### Python Style
- Use docstrings for all functions (triple quotes format)
- Follow PEP 8 naming conventions (snake_case for functions/variables)
- Use type hints where appropriate
- Include inline comments for complex logic

### API Endpoints
- Use RESTful conventions
- Return JSON responses with descriptive messages
- Use appropriate HTTP status codes:
  - 200: Success
  - 400: Bad request (validation errors, business logic errors)
  - 404: Resource not found
- Raise `HTTPException` for error cases with detailed messages

### Data Management
- In-memory data structures (dictionaries) for storing activities and student information
- Use sets for efficient skill management (O(1) operations)
- Email addresses use the pattern: `username@mergington.edu`

### Email Validation
- Email pattern: `r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'`
- Always validate email format using regex match

## Testing Guidelines

### Test Organization
- All tests go in `tests/test_app.py`
- Use pytest framework
- Use FastAPI's `TestClient` for API testing
- Tests should be independent and clean up after themselves

### Test Naming
- Test functions start with `test_`
- Use descriptive names: `test_<action>_<expected_outcome>`
- Examples: `test_signup_success`, `test_signup_duplicate`

### Test Structure
- Always include docstrings for test functions
- Use clear assertions with meaningful messages
- Clean up test data after tests (delete created resources)
- Test both success and error cases

### Test Coverage
When adding new features, ensure tests cover:
- Happy path (successful operations)
- Error cases (invalid input, not found, conflicts)
- Edge cases (capacity limits, validation failures)
- Data persistence expectations

## Common Patterns

### Activity Structure
Each activity must include:
- `description`: String describing the activity
- `schedule`: String with meeting times
- `max_participants`: Integer for capacity limit
- `participants`: List of email addresses
- `skills`: List of skills gained from the activity

### Error Handling
```python
if condition_not_met:
    raise HTTPException(status_code=4xx, detail="Clear error message")
```

### Path Parameters
Use URL path parameters for resource identifiers:
```python
@app.post("/activities/{activity_name}/signup")
```

### Query Parameters
Use query parameters for filters and optional data:
```python
def signup_for_activity(activity_name: str, email: str):
```

## Development Workflow

### Running Tests
```bash
pytest
```

### Running the Application
```bash
uvicorn src.app:app --reload
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

## Important Business Rules
1. Students can only sign up for an activity once
2. Activities have maximum capacity limits
3. Skills are added when students sign up for activities
4. Skills persist even after unregistering from activities
5. All student emails must be validated before processing

## When Making Changes
- Always run tests after making code changes
- Ensure backward compatibility with existing endpoints
- Update tests when modifying API behavior
- Keep the in-memory data structures synchronized
- Validate all input data appropriately
