# Use a lightweight base image with Python
FROM python:3.10-slim

# Set working directory in the container
WORKDIR /app

# Copy only necessary files
COPY ./api /app/api
COPY ./models /app/models
# Copy model dependencies into image
COPY ./models/models_dump_for_Registry /app/models/models_dump_for_Registry

# Install system dependencies for LightGBM
RUN apt-get update && apt-get install -y libgomp1

# Install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r api/requirements.txt

# Expose FastAPI's default port
EXPOSE 8000

# Run the FastAPI app with uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
