FROM node:18.1.0 as build

WORKDIR /repo

COPY package*.json ./

RUN npm install

COPY . .

RUN npm run build

FROM nginxinc/nginx-unprivileged:1.21.6

COPY --from=build /repo/dist /usr/share/nginx/html
