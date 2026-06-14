# GitScribe

GitScribe is an AI-powered developer tool that generates conventional commit messages and professional GitHub pull request descriptions from your git diffs.

## Tech Stack

- **Frontend:** Next.js (App Router), React, Tailwind CSS v4, TypeScript
- **Backend:** FastAPI, Python, Google GenAI SDK (Gemini API)

## Prerequisites

- Node.js (v18+ recommended)
- Python (3.10+ recommended)
- A Gemini API Key from Google AI Studio

## Setup Instructions

### 1. Configure Environment Variables

Create a `.env` file in the root directory (or use the one already provided) and add your Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 2. Backend Setup (FastAPI)

1. Open a terminal and navigate to the `backend` directory.
2. Activate the virtual environment (it has already been created for you):
   - **Windows:** `.\venv\Scripts\activate`
   - **macOS/Linux:** `source venv/bin/activate`
3. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

### 3. Frontend Setup (Next.js)

1. Open a new terminal and navigate to the `frontend` directory.
2. Install dependencies (if not already installed during scaffold):
   ```bash
   npm install
   ```
3. Start the Next.js development server:
   ```bash
   npm run dev
   ```
4. Open your browser to [http://localhost:3000](http://localhost:3000).

## Usage

1. Run `git diff` in your repository.
2. Copy the output and paste it into the "Git Diff Input" textarea in GitScribe.
3. Click **Generate Description**.
4. The AI will instantly generate a Conventional Commit message and a comprehensive PR description. Use the "Copy" buttons to quickly grab the output.

## Design

The UI uses a developer-focused, Vercel-inspired stark black-and-ink aesthetic with geometric sans fonts for readability and monospace fonts for technical labels. Dark mode is enabled by default.
