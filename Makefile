.PHONY: install clean

install:
	@pip install -r requirements.txt

clean:
	@echo "Cleaning up background services..."
	@PID=$$(lsof -t -i :8003); \
	if [ -n "$$PID" ]; then kill $$PID; fi
	@PID=$$(lsof -t -i :8321); \
	if [ -n "$$PID" ]; then kill $$PID; fi
	@PID=$$(lsof -t -i :8000); \
	if [ -n "$$PID" ]; then kill $$PID; fi
	@PID=$$(lsof -t -i :8501); \
	if [ -n "$$PID" ]; then kill $$PID; fi
