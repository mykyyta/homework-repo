# Use the official Python image from DockerHub
FROM python:3.12-slim

# Set the working directory insidocker build -t flaskapp .de the container
WORKDIR /app

# Copy requirements.txt (list of dependencies) into the container
COPY requirements.txt requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files into the container
COPY . .

# Expose the port your Flask app runs on
EXPOSE 5001

# Command to run the Flask app
CMD ["python", "app.py"]
#CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]