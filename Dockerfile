# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the default port (can be overridden)
ENV PORT=8501
EXPOSE $PORT

# Define the OpenAI API Key as a build argument
ARG OPENAI_API_KEY
ENV OPENAI_API_KEY=$OPENAI_API_KEY

# Run the indexer to build the local FAISS index based on current sample_docs
RUN python indexer.py

# Healthcheck to verify the Streamlit app is running
HEALTHCHECK CMD curl --fail http://localhost:${PORT}/_stcore/health || exit 1

# Command to run the application using env variable for port
CMD ["sh", "-c", "streamlit run app.py --server.port=${PORT} --server.address=0.0.0.0"]
