FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

# Tomar argumento VITE_API_URL
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
