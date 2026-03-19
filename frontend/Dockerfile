# Use an official Node.js runtime as a parent image
FROM node:18

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
# This leverages Docker's layer caching
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application's source code
COPY . .

# Make port 5173 available to the world outside this container (Vite's default port)
EXPOSE 5173

# Run the Vite dev server
# The --host flag is crucial to expose the server outside the container
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
