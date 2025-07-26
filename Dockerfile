FROM python:3.10-slim

# System dependencies
RUN apt-get update && apt-get install -y \
    curl \
    nodejs \
    npm \
    && apt-get clean

# Set working dir
WORKDIR /app

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Hardhat and Ganache CLI
RUN npm install -g hardhat

# Copy entire project
COPY . .

# Compile Hardhat contracts
WORKDIR /app/backend/hardhat_project
RUN npx hardhat compile

# Set workdir back to root
WORKDIR /app

# Streamlit entrypoint
CMD ["streamlit", "run", "frontend/app.py"]
