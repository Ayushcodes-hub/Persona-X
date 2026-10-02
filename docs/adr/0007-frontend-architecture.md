# ADR 0007: Frontend Architecture, Visual Design, and Evidence Graph Rendering

## Status
Accepted

## Context
The user interface must convey the gravitas, depth, and precision of a defense-grade public intelligence system. It must render large interconnected evidence graphs (nodes for persons, sources, evidence, claims, statements), live research streaming feeds, multi-dimensional political spectrums, and source inspection drawers with sub-second responsiveness.

## Decision
1. **Framework & Tooling**:
   - React 18 with TypeScript and Vite.
   - Tailwind CSS for modern utility styling, dark-first intelligence aesthetic, glassmorphic surfaces, and curated typography (Inter / JetBrains Mono).
   - Lucide React for consistent, crisp iconography.
2. **Evidence Graph Rendering**:
   - Use an optimized HTML5 Canvas / 2D interactive force-directed graph renderer with smooth pan/zoom, node physics, tier-based color coding (cyan for persons, blue for sources, emerald for verified evidence, amber for claims, purple for statements), and instant node inspection.
   - Avoid heavy DOM/SVG bottlenecks when rendering graphs with hundreds of nodes.
3. **State Management & Streaming**:
   - Lightweight reactive state management (Zustand or custom typed reactive store) for research session state, active person selection, and UI panels.
   - Built-in SSE connection manager with auto-reconnect, heartbeat detection, and event buffering for the Live Research HUD.
4. **Production Delivery & Single Page Application Routing**:
   - Client-side navigation supporting deep-linking (`/`, `/persons/:id`, `/research/:id`, `/observability`).
   - Unified build targeting `frontend/dist`, served either via Vercel / Cloudflare Pages or directly by the FastAPI backend under static mount with catch-all fallback.

## Consequences
- **Positive**: Blazing fast UI; 60fps graph exploration; cinematic dark aesthetic; zero UI lag during real-time streaming.
- **Negative**: Canvas-based graph requires manual touch/mouse event coordinate projection for hover tooltips.
