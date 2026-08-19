# VidhiSakha

VidhiSakha is a full-stack legal research and assistance platform built with a Next.js frontend and a Python FastAPI backend. The project appears to support legal research workflows such as browsing cases, statutes, a library, research tools, chat, help pages, and a secure vault-like area.

## Features

- Next.js-based web client
- FastAPI-based backend
- Legal research-oriented UI sections:
  - Cases
  - Statutes
  - Research
  - Library
  - Chat
  - Help
  - Vault
- Modern component stack with:
  - React 19
  - TypeScript
  - Tailwind CSS 4
  - shadcn/ui
  - React Hook Form
  - Zod validation
  - TanStack Query
  - Zustand
- Backend dependencies for AI / NLP / ML workflows:
  - sentence-transformers
  - transformers
  - torch
  - scikit-learn
  - lightgbm
  - ollama
- Utility scripts for debugging ranking and scoring logic

## Tech Stack

### Frontend
- Next.js 16
- React 19
- TypeScript
- Tailwind CSS 4
- shadcn/ui
- Lucide icons
- TanStack Query
- Zustand
- React Hook Form
- Zod

### Backend
- FastAPI
- Uvicorn
- python-dotenv
- psycopg2-binary
- pandas
- numpy
- requests
- sentence-transformers
- torch
- transformers
- scikit-learn
- lightgbm
- joblib
- ollama

## Repository Structure

```text
VidhiSakha/
├── client/                 # Next.js frontend
│   ├── src/
│   │   ├── app/            # App Router pages
│   │   ├── components/     # Shared UI components
│   │   ├── lib/            # Utility helpers
│   │   ├── services/       # API/service layer
│   │   └── types/          # Type definitions
│   ├── public/             # Static assets
│   └── package.json
├── server/                 # FastAPI backend
│   ├── core/
│   │   ├── api/
│   │   ├── embeddings/
│   │   ├── ingestion/
│   │   ├── persistence/
│   │   └── reasoning/
│   ├── dataset/
│   ├── docs/
│   ├── models/
│   ├── specs/
│   ├── tests/
│   └── requirements.txt
└── README.md
```

## Client

The frontend is a Next.js app under `client/`.

### Main scripts

```bash
npm run dev
npm run build
npm run start
npm run lint
```

### Client pages

From the repository structure, the app includes routes or sections such as:

- `/`
- `/chat`
- `/cases`
- `/help`
- `/library`
- `/login`
- `/research`
- `/statutes`
- `/vault`

## Server

The backend is a Python service under `server/` built around FastAPI and machine learning/NLP tooling.

### Likely responsibilities
- Exposing API endpoints
- Handling document ingestion
- Generating embeddings
- Supporting retrieval and reasoning workflows
- Persisting data
- Running search/ranking or LTR-related experiments

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the backend

If the FastAPI app entrypoint is available in your backend module, a typical startup command would be:

```bash
uvicorn main:app --reload
```

If your actual app module differs, replace `main:app` with the correct import path.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/rexysans/VidhiSakha.git
cd VidhiSakha
```

### 2. Set up the frontend

```bash
cd client
npm install
npm run dev
```

### 3. Set up the backend

```bash
cd ../server
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Then start the API server with the appropriate Uvicorn command.

## Environment Variables

The project likely uses environment variables for backend configuration. Common examples may include:

- `DATABASE_URL`
- `OPENAI_API_KEY` or other model provider keys
- `OLLAMA_HOST`
- `API_BASE_URL`

Add a `.env` file in the backend if required by your local setup.

## Development Notes

- The frontend is built with the Next.js App Router.
- The backend includes ML/NLP libraries, suggesting search, ranking, embeddings, or legal-retrieval features.
- There are debug scripts in the backend for LTR and score inspection, indicating experimentation with retrieval quality and ranking.
- The project appears to be actively structured for modular growth.

## Contributing

1. Create a feature branch
2. Make your changes
3. Run frontend and backend checks
4. Submit a pull request

## License

No license file was detected in the repository.

## Acknowledgements

Built with:
- Next.js
- React
- FastAPI
- Tailwind CSS
- shadcn/ui
- Hugging Face ecosystem
- scikit-learn
- LightGBM
