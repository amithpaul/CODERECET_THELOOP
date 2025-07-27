FROM python:3.10-slim

# System dependencies
RUN apt-get update && apt-get install -y curl nodejs npm \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working dir
WORKDIR /app

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project (ignore node_modules/artifacts via .dockerignore)
COPY . .

# Compile Hardhat contracts
WORKDIR /app/backend/app/hardhat_project
COPY backend/app/hardhat_project/package*.json ./
RUN npm install @openzeppelin/contracts
RUN npm install
RUN npx hardhat compile

# Set workdir back to root
WORKDIR /app

# Streamlit entrypoint
CMD ["streamlit", "run", "frontend/app.py"]

