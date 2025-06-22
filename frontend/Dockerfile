# build env
FROM node:21.7.1-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . ./
RUN npm run build
CMD cp -r /app/* /app/result_build/ 2>/dev/null || true && sleep infinity
