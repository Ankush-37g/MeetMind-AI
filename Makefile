.PHONY: run backend frontend clean

# Run both frontend and backend concurrently
run:
	@echo "🚀 Starting MeetMind AI..."
	@make -j 2 backend frontend

# Start the FastAPI backend
backend:
	@echo "🐍 Starting backend on port 8000..."
	.venv/bin/uvicorn api:app --host 127.0.0.1 --port 8000 --reload

# Start the React frontend
frontend:
	@echo "⚛️  Starting frontend on port 5173..."
	cd frontend && npm run dev

# Clean up caches and temp files
clean:
	@echo "🧹 Cleaning up..."
	rm -rf __pycache__ .pytest_cache
	rm -rf frontend/node_modules frontend/dist
	rm -rf downloads/*
	@echo "✅ Clean complete!"
