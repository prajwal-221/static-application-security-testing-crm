# Use Node.js 20 LTS
FROM node:20-alpine

# Create app directory
WORKDIR /usr/src/app

# Copy dependency files first (better caching)
COPY package*.json ./

# Install dependencies
RUN npm install --production

# Copy app source
COPY . .

# Expose the port the app runs on
EXPOSE 4000

# Start application
CMD ["npm", "start"]
