# Use Node.js 20 LTS
FROM node:20-alpine

# Create app directory
WORKDIR /usr/src/app

# Copy package files and .env
COPY package*.json ./
COPY .env ./

# Install dependencies
RUN npm install

# Bundle app source
COPY . .

# Expose the port the app runs on
EXPOSE 4000

# Command to run the application
CMD ["sh", "-c", "npm run setup && npm run dev"]
