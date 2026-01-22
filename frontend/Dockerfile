# Use Node.js 20 LTS
FROM node:20-alpine as build

# Create app directory
WORKDIR /usr/src/app

# Define build arguments
ARG VITE_BACKEND_SERVER
ENV VITE_BACKEND_SERVER=$VITE_BACKEND_SERVER

# Copy package files
COPY package*.json ./


# Install dependencies
RUN npm install

# Bundle app source
COPY . .

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets from build stage
COPY --from=build /usr/src/app/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
