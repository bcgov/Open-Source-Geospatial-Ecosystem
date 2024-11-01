FROM python:3.11

# Set up environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy only the requirements file first to leverage Docker caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# add app folder contents to WORKDIR
COPY app ./app
COPY data ./data

# Expose the port your application will run on
EXPOSE 5000

# Specify the command to run on container start
WORKDIR /app
CMD ["gunicorn","--timeout", "500","--bind","0.0.0.0:5000","--workers","2","app:app"]
