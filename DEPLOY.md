# Docker / Docker Compose deployment for chanlun_pro backend (updated with Postgres example)

Quick start (Postgres)

1. Copy example env and (optionally) customize credentials:
   cp .env.postgres.example .env

2. Build and run with docker-compose (from repository root):

   docker-compose up --build -d

3. Check logs:

   docker-compose logs -f backend

4. Stop:

   docker-compose down

Notes

- The compose file now includes a postgres service. By default the backend's DATABASE_URL is set to:
  postgresql://chanlun:changeme@db:5432/chanlun
  and the postgres service uses the same credentials. Change these in .env before starting.

- The backend will create DB tables on startup using SQLAlchemy's Base.metadata.create_all(). No manual migrations are required for the initial schema, but for production you should use alembic or a proper migration tool.

- For local/simple usage you can still use SQLite by setting DATABASE_URL=sqlite:///./chanlun.db in the environment (either in .env or docker-compose override). The docker-compose mounts ./chanlun.db into the container so the file persists on the host.

Security

- Do not commit .env with real passwords. Use environment variables or secret managers for production.

If you'd like, I can next:
- Add a small DB migration setup (alembic) and migration script
- Add a GitHub Actions workflow to build and push images
- Harden the backend (retries, logging, health endpoint)
