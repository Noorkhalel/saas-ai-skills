FROM node:latest

WORKDIR /app

COPY . .

ENV NPM_TOKEN=npm_9aFk2LmQ8xZ0pRtVwYbNcDeFgHiJkLmNoPq
ENV DATABASE_URL=postgres://admin:S3cr3tP@ss@db.prod.internal/main

RUN npm install
RUN npm run build

EXPOSE 3000

CMD ["node", "server.js"]
