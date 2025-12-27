FROM python:3.13-alpine
WORKDIR /usr/local/app

# Install the application dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy in the source code
COPY app.py config.py ./
COPY cogs ./cogs

# Setup a bot user so the container doesn't run as the root user
RUN addgroup -S botgroup && adduser -S bot -G botgroup

# Change ownership to the bot user for all files
RUN chown -R bot:botgroup /usr/local/app

# Only change permissions for data.json if it already exists
RUN [ -f /usr/local/app/data.json ] && chown bot:botgroup /usr/local/app/data.json && chmod 664 /usr/local/app/data.json || echo "data.json not found, skipping"

USER bot

CMD ["python", "-u", "app.py"]