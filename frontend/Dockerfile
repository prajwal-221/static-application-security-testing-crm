# Build stage
FROM node:20-alpine AS builder

WORKDIR /usr/src/app

ARG VITE_BACKEND_SERVER
ENV VITE_BACKEND_SERVER=$VITE_BACKEND_SERVER

COPY package*.json ./
RUN npm install

COPY . .

RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets
COPY --from=builder /usr/src/app/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
