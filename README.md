# DeFi Risk Dependency Analyzer — Phase 1

A brutalist, monochrome single-page application for analyzing risk propagation
across interconnected DeFi protocol layers. Phase 1 uses mock data and
deterministic simulations to establish a clean, extensible foundation.

> **Disclaimer** — All values are illustrative. This is not financial advice.

---

## Project Structure

```
bsa/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── requirements.txt     # Python dependencies
│   └── venv/                # Python virtual environment (generated)
│
├── frontend/
│   ├── app/
│   │   ├── globals.css      # Monochrome design system
│   │   ├── layout.tsx       # Root layout
│   │   └── page.tsx         # Main page (state management)
│   ├── components/
│   │   ├── TargetInput.tsx
│   │   ├── DependencyGraph.tsx
│   │   ├── DependencyNode.tsx
│   │   ├── TerminalLogs.tsx
│   │   └── VerdictDashboard.tsx
│   ├── lib/
│   │   ├── api.ts           # Backend API client
│   │   ├── simulation.ts    # Mock simulation logic
│   │   └── types.ts         # Shared TypeScript types
│   ├── .env.local.example
│   ├── tailwind.config.ts
│   └── package.json
│
└── README.md
```

---

## Quick Start

### 1. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

The backend is now running at **http://localhost:8000**.

### 2. Frontend

```bash
cd frontend
cp .env.local.example .env.local   # sets NEXT_PUBLIC_API_URL
npm install
npm run dev
```

The frontend is now running at **http://localhost:3000**.

---

## Verify the Connection

### Health check

```bash
curl http://localhost:8000/api/health
# {"status":"ok"}
```

### Analyze (valid address)

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"token_address": "0x1234567890abcdef"}'
# {"status":"success","token_address":"0x1234567890abcdef",
#  "slippage":0.11,"expected_loss":50000.0,"action":"EXIT"}
```

### Analyze (empty — expect 422)

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"token_address": ""}'
# 422 Unprocessable Entity
```

### Analyze (whitespace-only — expect 422)

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"token_address": "   "}'
# 422 Unprocessable Entity
```

---

## Interaction Checklist

| # | Action | Expected Result |
|---|--------|-----------------|
| 1 | Open http://localhost:3000 | Monochrome page loads |
| 2 | Click [ ANALYZE ] with empty input | Nothing happens (button disabled) |
| 3 | Type address, click [ ANALYZE ] | Terminal logs appear, dashboard shows 11.00% / $50,000 / EXIT |
| 4 | Expand terminal | Timestamped logs visible |
| 5 | Click a dependency node | Node turns black, verdict updates |
| 6 | Click [ RESET ] | Nodes reset, verdict restores backend baseline |
| 7 | Click [ CLEAR ] in terminal | Logs cleared |
| 8 | Stop backend, click [ ANALYZE ] | Error appears in terminal |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend base URL |

---

## Design Rules

- Black `#000000` and white `#FFFFFF` only
- Monospace font (Courier New) everywhere
- No rounded corners, shadows, gradients, or colors
- Sharp 1px black borders
