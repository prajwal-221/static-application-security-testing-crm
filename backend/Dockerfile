# Use Node.js 20 LTS
FROM node:20-alpine

# Create app directory
WORKDIR /usr/src/app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy app source
COPY . .

# Expose port
EXPOSE 4000

# Run app
CMD ["sh", "-c", "npm run setup && npm start"]
