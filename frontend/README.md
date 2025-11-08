Frontend scaffold instructions

Option A (recommended for full React frontend):

1. Install Node.js (>=16) and npm or pnpm.
2. From the project root run:

npx create-react-app frontend --template cra-template-pwa
cd frontend
npm install
npm start

This creates a `frontend/` React app. You can then implement forms and results UI and point API calls to the Flask backend (http://localhost:5000).

Option B (quick Bootstrap static prototype):

Create `frontend/index.html` with Bootstrap and a simple form to POST to the Flask backend. This is faster for early testing without a full React toolchain.

Notes
- If you create the React app, add `/frontend/node_modules` to `.gitignore` (already included).
- Configure a proxy in `frontend/package.json` (e.g. "proxy": "http://localhost:5000") for local development to avoid CORS issues.
