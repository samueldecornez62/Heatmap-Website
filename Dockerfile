# Use Python 3.9 slim as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files into the container
COPY . /app/

# Copy the .pkl files into the container
COPY sorted_covariance.pkl /app/
COPY universe_covariance.pkl /app/

# Expose the port the app will run on
EXPOSE 8050

# Define the command to run the app
CMD ["python", "more_test.py"]
