# Stage 1: Build Stage
FROM python:3.8-alpine as build

# Install build dependencies
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev nodejs npm

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python and npm dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    npm install

# Run the build script
RUN npm run build-css

# Remove build dependencies to reduce image size
RUN apk del gcc musl-dev

# Stage 2: Runtime Stage
FROM python:3.8-alpine

# Set the working directory in the container to /app
WORKDIR /app

# Copy only the necessary files from the build stage
COPY --from=build /app /app

# Install runtime dependencies
RUN apk add --no-cache libstdc++ libffi openssl

# Install gunicorn
RUN pip install --no-cache-dir gunicorn

# Install Python packages from requirements.txt (copied from build stage)
COPY --from=build /usr/local/lib/python3.8/site-packages /usr/local/lib/python3.8/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

# Clean up unnecessary files to keep the image size small
RUN rm -rf /var/cache/apk/* /root/.cache /tmp/* /usr/share/man /usr/share/doc /usr/include /app/node_modules /app/package.json /app/package-lock.json /app/webpack.config.js

# Set environment variables for production
ENV FLASK_DEBUG=0
ENV PYTHONUNBUFFERED=1

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run gunicorn server when the container launches
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
