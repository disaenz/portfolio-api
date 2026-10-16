# 📡 Portfolio API

The **Portfolio API** is a modern, serverless backend powering personal projects, portfolio automation, and future AI-driven features. Built with **FastAPI**, containerized with **Docker**, and deployed to AWS Lambda as a scalable container-image service.

This API originally started as a backend for grant operations and is now evolving into the centerpiece of a personal cloud portfolio ecosystem.

---

## ✨ Key Features

🔹 Serverless — zero idle compute cost  
🔹 High-performance **FastAPI** backend  
🔹 PostgreSQL relational persistence  
🔹 Automated CI/CD builds and scans  
🔹 Designed for modular expansion (AI + portfolio insights)

---

## 🧩 Architecture Overview

| Layer | Technology |
|-------|------------|
| Application Framework | FastAPI (Python 3.12) |
| Containerization | Docker |
| Deployment Target | AWS Lambda (Container Image) |
| Database | NeonDB (PostgreSQL) |
| CI/CD | GitHub Actions |
| Security | Trivy vulnerability scanning |

📙 Live API Docs:  
https://api.daniel-saenz.com/docs

---

## 🔌 Current Endpoints

| Route | Method | Description |
|-------|--------|-------------|
| `/api/grants` | GET | List all grants *(example/demo resource)* |
| `/api/grants/{id}` | GET | Fetch a grant by ID *(example/demo resource)* |
| `/api/grants` | POST | Create a new grant *(example/demo resource)* |
| `/api/grants/{id}` | PATCH | Update a grant *(example/demo resource)* |
| `/api/ai` | GET | Health check for the AI service |
| `/api/ai/chat` | POST | Ask questions about Daniel’s professional background (AI-powered) |

---

## 💻 Local Development

1. **Clone the repository**

   ```bash
   git clone https://github.com/disaenz/porfolio-api.git
   cd portfolio-api
   ```

2. **Install dependencies**
(Recommended: use a Python virtual environment)

    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

3. **Run the complete local stack**

    The API repository's Compose file starts an isolated PostgreSQL instance,
    applies `migrations/schema.sql` and repeatably seeds `migrations/mock_data.sql`, and
    starts both the API and the sibling `portfolio-site` repository with hot
    reload enabled.

    ```bash
    cp .env.example .env # fill in OPENAI_API_KEY; retain any SES values you use
    ./run_dev.sh
    ```

    - Site: http://localhost:5173
    - API and docs: http://localhost:8010/docs
    - Local PostgreSQL: `localhost:5434` (`portfolio` / `portfolio`, database `portfolio_local`)

    The stack starts in the background. View logs with `docker compose logs -f`;
    stop it with `docker compose down`. To remove the local database as well,
    run `docker compose down -v`.

4.	**Test API endpoints**

    The interactive Swagger UI will auto-generate docs and let you test endpoints.

---

## 🤖 Refreshing AI knowledge

The assistant no longer reads a checked-in JSON file. Its current knowledge is
stored as JSONB in PostgreSQL. After publishing a site or resume update, run:

```bash
./refresh_local_knowledge.sh
```

The command reads `https://daniel-saenz.com` by default, discovers the public
Dropbox resume link from the site bundle (or uses `PORTFOLIO_RESUME_URL`), and
uses `OPENAI_MODEL` (default: `gpt-6-luna`) to produce the existing portfolio-knowledge shape before
upserting it into the local database. It also writes the pretty-printed result
to ignored `data/portfolio_knowledge.json` for local inspection. It requires
the Compose stack and a valid `OPENAI_API_KEY`. Set `PORTFOLIO_SITE_URL` if you
want to refresh from a different deployed environment. The command shows
five progress steps while it reads the sources, generates the JSON, and saves it.
AWS runs the same image as a separate `portfolio-knowledge-refresh` Lambda at
8:00 AM America/Denver each day. It exits before calling OpenAI when the source
hash is unchanged. If a refresh fails, it emails `RECIPIENT_EMAIL` from
`SES_SENDER_EMAIL` using the existing SES service, then re-raises the error so
EventBridge retries and CloudWatch records the failure.

For a non-container environment, run the same Python entry point after applying
the schema and setting `DATABASE_URL`:

```bash
python scripts/refresh_portfolio_knowledge.py
```

---

## 🔒 Security & Quality

*	Trivy scans every Docker image for vulnerabilities during CI
*	IAM roles: Follows least-privilege for ECR push/pull and Lambda deploy
*	Terraform: All AWS infrastructure is managed as code

---

## 🚀 CI/CD Pipeline

This repository includes a complete GitHub Actions pipeline:
1.	Build & Push: Builds and pushes Docker images to AWS ECR
2.	Vulnerability Scan: Uses Trivy to check the image for CRITICAL vulnerabilities
3.	Cleanup: Automatically deletes old/dangling ECR images
4.	Deploy: Updates the AWS Lambda function with the new image

All sensitive values (ECR repo, image URI, AWS credentials) are stored as GitHub Secrets.
Set the non-secret `OPENAI_MODEL` GitHub Actions repository variable to choose
the model deployed to Lambda; it defaults to `gpt-6-luna`.

When a pull request or push changes `migrations/**`, CI applies
`migrations/schema.sql` to a disposable PostgreSQL service. On a successful
push to `main`, CD applies both `schema.sql` and `mock_data.sql` to Neon before
updating Lambda. The mock-data seed removes and reinserts only its six known
demo grants, so it can be safely reapplied without duplicates.
Add a `DATABASE_URL` GitHub Actions secret using the application's production
database URL. CD converts the `postgresql+asyncpg://` form to the standard
`postgresql://` form required by `psql`. `PSQL_URL` remains optional and is
only used by the local `connect_neon.sh` convenience script.

To open a direct Neon `psql` session using the local `.env` value, run:

```bash
./connect_neon.sh
```

---

## 📝 Deployment Notes
* Production deploys occur automatically on push to main.
* PRs/feature branches: Full build & scan runs, but deploy only happens on main.

---

## 📜 Fork & Attribution

This repository is a personal portfolio maintained by Daniel Saenz. Feel free to fork and adapt it for your own use. If you do, please credit the original author in your project documentation or README.
This project is open source under the [MIT License](./license.md). 

---

© 2025 Daniel Saenz
