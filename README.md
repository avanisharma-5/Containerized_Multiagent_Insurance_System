# Insurance Multi-Agent Project

## Structure

- `backend/` FastAPI + CrewAI agents + RAG + chat history + image generation endpoint
- `frontend/` Streamlit client

## Local Run

1. Create env file:
   - Copy `backend/.env.example` to `backend/.env`
2. Install backend deps:
   - `pip install -r backend/requirements.txt`
3. Run backend:
   - `uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload`
4. Install frontend deps:
   - `pip install -r frontend/requirements.txt`
5. Run frontend:
   - `streamlit run frontend/app.py`

## Main Endpoints

- `POST /chat/session`
- `POST /files/upload`
- `POST /workflow/run`
- `POST /images/generate`

## AWS Deployment Notes

- Easiest path: deploy backend as one container on ECS/App Runner/Elastic Beanstalk.
- Keep `frontend/` static files on S3 + CloudFront.
- Set all env vars in AWS service config (not in image).
- Use an EBS/EFS volume or S3-backed strategy if you need persistent upload/history across restarts.
