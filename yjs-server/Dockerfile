# ./yjs-server/Dockerfile
FROM node:18-slim

# Устанавливаем рабочую директорию
WORKDIR /usr/src/app

# Копируем package.json и package-lock.json (если есть)
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем остальной код
COPY . .

# Устанавливаем переменные окружения
ENV PORT=1234
ENV HOST=0.0.0.0
ENV CALLBACK_URL=http://backend:8000/api/v1/yjs/callback 
ENV REDIS_URL=redis://redis:6379
ENV VERIFY_URL=http://backend:8000/api/v1/yjs/verify-connection

EXPOSE 1234

# Запускаем наш кастомный сервер
CMD ["npm", "start"]
