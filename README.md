# Grant API

Welcome to the **Grant API** — a serverless, containerized REST API for managing grant-related operations, built with FastAPI and deployed to AWS Lambda using Docker and ECR. This project showcases modern Python backend practices, secure infrastructure-as-code, and automated CI/CD pipelines.

---

## 🚀 Project Overview

The Grant API provides a fast, serverless backend designed to be cost-efficient, scalable, and easy to maintain. It supports:

* **REST endpoints** for grant data operations (CRUD, querying, etc)
* **FastAPI** for type-safe, high-performance Python APIs
* **Database integration** (PostgreSQL, Neon, or any Postgres-compatible cloud DB)
* **CI/CD** with security scanning, automated ECR cleanup, and one-command Lambda deployment
* **Modern DevSecOps** practices: Docker, Trivy scanning, least-privilege IAM, IaC for ECR/Lambda roles

---

## 🛠 Technologies

* **API Framework**: FastAPI (Python 3.12)
* **Containerization**: Docker, AWS ECR
* **Serverless Compute**: AWS Lambda (Container Image)
* **Database**: PostgreSQL (via asyncpg + SQLAlchemy)
* **CI/CD**: GitHub Actions
* **Security & Quality**: Trivy (image vulnerability scanning), IAM least-privilege policies
* **Infrastructure as Code**: Terraform (for ECR, Lambda, IAM roles/policies)

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

3.	**Run locally**

    ```bash
    uvicorn main:app --reload
    ```

    The API will be available at http://localhost:8000

4.	**Test API endpoints**

    The interactive Swagger UI will auto-generate docs and let you test endpoints.

---

## 🐳 Docker Usage

1.	**Build Docker image**

    ```bash
    docker build -f Dockerfile.local -t portfolio-api:latest .
    ```

2.	**Run Docker container locally**

    ```bash
    docker run -p 8000:8080 portfolio-api:latest
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