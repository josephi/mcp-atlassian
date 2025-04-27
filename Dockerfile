# Use a Python image with uv pre-installed
FROM python:3.10-slim AS uv

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install uv using pip
RUN pip install uv

# Copy project files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-install-project --no-dev --no-editable

# Then, add the rest of the project source code and install it
COPY . .
RUN uv sync --frozen --no-dev --no-editable

FROM python:3.10-slim

WORKDIR /app

COPY --from=uv --chown=app:app /app/.venv /app/.venv

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["mcp-atlassian"]
