# Workers

The worker boundary exposes `GET /health` on port `8010` and is ready for
background jobs such as crawling, parsing, embeddings, resume generation, and
notifications. The `POST /jobs/notifications` endpoint is the scheduler
boundary for reminder delivery. Run it locally with:

```bash
pip install -r requirements.txt
uvicorn worker:app --host 0.0.0.0 --port 8010
```
