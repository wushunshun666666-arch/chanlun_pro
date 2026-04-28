# Docker / Docker Compose deployment for chanlun_pro backend

This file describes how to run the FastAPI backend in Docker using the provided Dockerfile and docker-compose.yml.

Quick start (build + run)

1. Build and run with docker-compose (from repository root):

   docker-compose up --build -d

2. Check logs:

   docker-compose logs -f backend

3. Stop:

   docker-compose down

Notes

- By default the service uses a SQLite file at ./chanlun.db (mounted into the container). For production you should use PostgreSQL or another managed DB.
- To use Postgres, uncomment the `db` service in docker-compose.yml and set `DATABASE_URL=postgresql://chanlun:changeme@db:5432/chanlun` in the backend environment section (or set DATABASE_URL via your environment or secret manager).
- The container exposes port 8000 (uvicorn). You can put a reverse proxy (nginx) in front for TLS and better process management.
- Environment variables:
  - DATABASE_URL: SQLAlchemy connection string (default: sqlite:///./chanlun.db)
  - TZ: timezone (default Asia/Shanghai)

Security

- Do not store secrets such as DB passwords in git. Use environment variables or docker-compose override files / secret stores.

If you want, I can also:
- Add a systemd service file example to run docker-compose on startup
- Create a docker hub / GitHub Actions workflow for building and pushing images
