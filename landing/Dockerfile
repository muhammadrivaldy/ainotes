FROM node:20-alpine AS base
WORKDIR /app

# By default, listen on port 3000
ENV HOST=0.0.0.0
ENV PORT=3000
EXPOSE 3000

FROM base AS prod-deps
COPY package.json package-lock.json ./
RUN npm install --production

FROM base AS build-deps
COPY package.json package-lock.json ./
RUN npm install

FROM build-deps AS build
COPY . .
RUN npm run build

FROM base AS runtime
COPY --from=prod-deps /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist

CMD ["node", "./dist/server/entry.mjs"]

FROM nginx:alpine AS production
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
