# Deploying to Google AI Studio (quick)

1. Push this repo to GitHub.
2. In Google AI Studio, choose "New Project" → "Import from GitHub".
3. Select repo `nlp-hypnosis-sales-ai-studio`.
4. Configure environment: install dependencies from `requirements.txt`.
5. Start the app (use `uvicorn main:app --port 8080`) or deploy container via Docker.
6. Test endpoints (GET /packs, POST /get_pack) inside Studio's testing console.
7. Use /render_payload output as input to your visual builder or webapp.
