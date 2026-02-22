FROM node:20-slim

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Vite டெவலப்மெண்ட் சர்வர்
CMD ["npm", "run", "dev", "--", "--host"]