# Palmaray

<div style="background: #ffffff; padding: 16px 24px; display:flex; align-items:center; width:100%; box-sizing:border-box;">
	<img src="icons/icon.png" width="96" alt="Icon" style="margin-right:16px;" />
	<div>
		<h1 style="margin:0;">Palmaray</h1>
		<div style="color:#666; font-size:14px;">A self-hosted LLM bridge client for Telegram</div>
	</div>
</div>

<div style="margin-top:8px;">
	<img src="https://img.shields.io/badge/status-development-yellow?style=flat-square&logo=github" alt="development" />
</div>

Palmaray is a lightweight Telegram assistant that uses LLMs to generate responses, stores messages and topic embeddings in Postgres (with pgvector), and encrypts sensitive text fields at rest.

**Disclaimer**

This application was created because the author was tired of paying for subscriptions and prefers to use LLMs on a pay-as-you-go basis. It is a self-hosted application — you may use it for yourself and your family.

Please note that messages are stored on your server in encrypted form; treat the `SECRET_KEY` with care and responsibility. The author accepts no liability for the security or retention of your data — the application is provided "as is" without warranties.

**Purpose**
- Act as a bridge client for LLMs — turn a Telegram bot into a client for LLMs.
- Maintain short and long conversation history, archive/summarize content, and embed topics for retrieval.
- Secure sensitive message text using application-level encryption.

**Key components**
- `bot/` — Telegram handlers and bot startup.
- `llms/` — LLM models, repos and request orchestration.
- `messages/`, `users/` — persistence, services, and usecases.
- `lib/` — shared utilities (DB, encryption, repo helpers).
- `alembic/` — DB migrations.
- `docker/` — Dockerfiles for app and database (pgvector-enabled).

Requirements
- Python 3.11+ (project developed on 3.13)
- pipenv (used in repo)
- Docker & docker-compose (for containerized deployment)

Environment variables (.env)
- `DB_USER`
- `DB_PASS`
- `DB_NAME`
- `DB_HOST`
- `DB_PORT`
- `DB_SSL`
- `TG_TOKEN`
- `OPENAI_API_KEY`
- `SECRET_KEY`

Local development
1. Create and activate the virtualenv with pipenv:

```bash
pipenv install --dev
pipenv shell
```

2. Create `.env` in the project root with required variables.

3. Run static checks (from `Pipfile`):

```bash
pipenv run check
```

4. Apply database migrations:

```bash
pipenv run alembic upgrade head
```

5. Run the bot locally (use `Pipfile` script):

```bash
pipenv run main
```

Docker / Production
- A Docker image for Postgres with `pgvector` is provided under `docker/postgres`; `docker-compose.yaml` defines `database` and `app` services.

Build and run with:

```bash
docker compose up --build -d database app
```

After the database comes up, run migrations from the host (or via the app container):

```bash
pipenv run alembic upgrade head
```

Notes and gotchas
- Alembic migrations include population of default LLM rows and will add the `provider` column. Back up production data before running migrations.
- Telegram messages are sent using MarkdownV2 in all handlers — verify client compatibility.
- Sensitive text is encrypted via a SQLAlchemy TypeDecorator; ensure `settings.SECRET_KEY` remains constant across deployments to allow decryption of stored records.
- If you update `pgvector` or the database image, rebuild the `database` service so the extension is available at migration time.

Support
- For quick tests use the `/llm_list` command to list LLMs and pick a model.

License & Attribution
- (Add license and attribution as needed)
