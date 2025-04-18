#!/bin/bash

echo "Starting Housing Data Loader Setup..."

echo "Setting up environment..."
pip install pymysql

echo "Loading housing data to MySQL..."
python3 housing_loader_package/load_to_mysql.py

# Step 1: Start Docker container for MySQL
echo "Launching MySQL container with Docker Compose..."
docker-compose up -d

# Wait a few seconds for MySQL to initialize
echo "Waiting for MySQL to initialize..."
sleep 10

# Step 2: Create the housing_data table
echo "Creating table in MySQL..."
docker exec -i mysql_housing_v2 mysql -u root -proot housing_db < housing_loader_package/create_table.sql
docker exec -i mysql_housing_v2 mysql -u root -proot housing_db < housing_loader_package/create_input_table.sql

# Step 3: Install Python dependencies
echo "Installing Python dependencies..."
pip install -r housing_loader_package/requirements.txt

# Step 4: Load the CSV data into MySQL
echo "Running the data loader script..."
python housing_loader_package/load_to_mysql.py

echo "Setup complete. Housing data successfully loaded!"
