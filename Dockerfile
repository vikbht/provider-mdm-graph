FROM python:3.11-slim

# Install uv
RUN pip install uv

WORKDIR /app

# Copy dependency definition
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
# --frozen ensures lockfile is respected
RUN uv sync --frozen

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code
COPY . .

# Default command matching new structure
CMD ["uv", "run", "uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
