# Housing Price Data Loader

This folder contains everything needed to set up and load the housing price data into a MySQL database.

---

## Quick Start

### Requirements
- Docker & Docker Compose installed
- Python 3.9+ and pip
- MySQL port 3307 **must be free**  **(note the change!!!!)**

---

### Setup Steps

#### 1. Start the MySQL container

From the repo root (`bt4301-group-5`):

```bash
docker-compose up -d
```

This will launch a MySQL container with:
- Host: `localhost`
- Port: `3307` **(note the change!!!!)**
- DB: `housing_db`
- User: `root` / Password: `root`

#### 2. Run the setup script

```bash
chmod +x housing_loader_package/setup.sh
./housing_loader_package/setup.sh
```

This will:
- Create the `housing_data` table
- Install required Python packages
- Load data from `enhanced_data.csv`

**NEW!!!!**
- Create the `input_data` table
- Load data from `user_input_data.csv`

---

### Verify Data in MySQL

Run:
```bash
docker exec -it mysql_housing_v2 mysql -u root -proot housing_db
```

Inside MySQL:

```sql
SHOW TABLES;
SELECT COUNT(*) FROM housing_data;
SELECT COUNT(*) FROM input_data;
SELECT * FROM housing_data LIMIT 5;
```

---

## Folder Contents

- `enhanced_data.csv`: Cleaned housing price dataset
- `user_input_data.csv`: simulated user input dataset
- `create_table.sql`: SQL to create the target table
- `create__input_table.sql`: SQL to create the user input table
- `load_to_mysql.py`: Script to insert CSV into MySQL
- `setup.sh`: One-click setup script
- `requirements.txt`: Python packages

---

## Maintainers

This module was prepared by the **DataOps team** as part of the final project pipeline.
