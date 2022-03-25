# Image for a Python 3 development environment
FROM python:3.9-slim

# Add any tools that are needed beyond Python 3.9
RUN apt-get update && \
    apt-get install -y sudo vim git zip tree curl wget jq && \
    apt-get autoremove -y && \
    apt-get clean -y

# Configure git
RUN git config --global user.name "Shantanu Dahiya" \
    && git config --global user.email "shantanu.webmail@gmail.com"

# Set up the Python development environment
WORKDIR /app
RUN python -m pip install --upgrade pip && \
    pip install --upgrade wheel

# Enable color terminal for docker exec bash
ENV TERM=xterm-256color
