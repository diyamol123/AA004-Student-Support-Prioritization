FROM node:24-alpine AS build

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

RUN npm run build

FROM nginx:alpine

ENV NGINX_ENVSUBST_FILTER=^BACKEND_URL$

COPY --from=build /app/dist /usr/share/nginx/html

COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template

EXPOSE 80
