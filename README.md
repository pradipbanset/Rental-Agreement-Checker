# Rental Agreement Checker

AI-powered rental agreement analyzer for Australian tenancy laws using Claude AI.

## Description

This application analyzes rental contracts to identify illegal clauses, unfair terms, and compliance issues across all Australian states (NSW, VIC, QLD, ACT, SA, WA, TAS, NT). Upload your rental agreement and get instant AI analysis with interactive chat support.

## How to Run

### 1. Clone and Setup
```bash
git clone https://github.com/pradipbanset/Rental-Agreement-Checker.git
cd Rental-Agreement-Checker
cp .env.example .env
```

### 2. Add API Keys to `.env`
```properties
CLAUDE_API_KEY=your-key-here
GOOGLE_CLIENT_ID=your-id-here
GOOGLE_CLIENT_SECRET=your-secret-here
SECRET_KEY=your-jwt-secret-here
```

Get keys from:
- Claude: https://console.anthropic.com/
- Google OAuth: https://console.cloud.google.com/

### 3. Run with Docker
```bash
docker-compose up --build
```

### 4. Access Application

- Frontend: http://localhost:3000
- Backend: http://localhost:8000

## Tech Stack

**Backend:** Python, FastAPI, PostgreSQL, Claude AI  
**Frontend:** React, Tailwind CSS
