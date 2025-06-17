.PHONY: install clean

install:
	@pip install -r requirements.txt
	@cd ../llama-stack/ && \
	rm -rf *.egg-info && \
	pip install -e .
	@cd ../llama-stack-client-python/ && \
	rm -rf *.egg-info && \
	pip install -e .

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
