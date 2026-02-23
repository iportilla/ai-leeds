.PHONY: install index run stop clean docker-build docker-run docker-stop

# Load environment variables from .env if it exists
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

# Default port if not specified in .env
PORT ?= 8502

install:
	python3 -m pip install -r requirements.txt

index:
	python indexer.py

run:
	python3 -m streamlit run app.py --server.port $(PORT) --server.address 0.0.0.0

stop:
	pkill -f "streamlit run app.py" || true

clean:
	rm -f vector_index.bin metadata.json

docker-build:
	docker build --build-arg OPENAI_API_KEY=$(OPENAI_API_KEY) -t leeds-ai-policy-advisor .

docker-run:
	docker run -d --name leeds-ai-policy-advisor -p $(PORT):$(PORT) -e PORT=$(PORT) --env-file .env leeds-ai-policy-advisor

docker-stop:
	docker stop leeds-ai-policy-advisor || true
	docker rm leeds-ai-policy-advisor || true
