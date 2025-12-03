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
| `/api/grants` | GET | List all grants |
| `/api/grants/{id}` | GET | Fetch a grant |
| `/api/grants` | POST | Create a new grant |
| `/api/grants/{id}` | PATCH | Update a grant |

More portfolio-focused services are in active development.

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