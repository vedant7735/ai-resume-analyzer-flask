FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Copy application files
COPY . .

# Expose Vite development port
EXPOSE 5173

# Run development server binding to host machine
CMD ["npm", "run", "dev"]
