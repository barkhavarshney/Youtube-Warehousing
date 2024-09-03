# YouTube-Warehousing

**Using Postgresql, MongoDB and Streamlit**

The YouTube Data Harvesting and Warehousing project is designed to empower users to access and analyze data from various YouTube channels. The application utilizes SQL, MongoDB, and Streamlit to create a user-friendly interface for retrieving, saving, and querying YouTube channel and video data.

## Tools and Libraries Used:

- **Streamlit:** 
  - This library is employed to develop a user-friendly UI that facilitates interaction with the program, allowing users to perform data retrieval and analysis operations.

- **Python:** 
  - The primary programming language used for the entire application, Python is known for its simplicity and power. It is employed for tasks such as data retrieval, processing, analysis, and visualization.

- **Google API Client:**
  - The googleapiclient library in Python is crucial for communicating with various Google APIs. In this project, it interacts with YouTube's Data API v3, enabling the retrieval of essential information like channel details, video specifics, and comments.

- **MongoDB:** 
  - This document database is chosen for its scale-out architecture, making it suitable for developing scalable applications with evolving data schemas. MongoDB simplifies the storage of structured or unstructured data using a JSON-like format.

- **PostgreSQL:** 
  - An open-source and highly scalable database management system, PostgreSQL is known for its reliability and extensive features. It provides a platform for storing and managing structured data, supporting various data types and advanced SQL capabilities.

## 📖 Ethical Perspective on YouTube Data Scraping
Engaging in YouTube data scraping demands ethical responsibility. It is crucial to:

- `Adhere to YouTube's terms of service.`
- `Obtain proper authorization and comply with data protection regulations.`
- `Handle data responsibly, ensuring privacy and avoiding misuse.`
- `Respect the YouTube community and the platform’s integrity.`

## Required Libraries:

- `googleapiclient.discovery`
- `streamlit`
- `psycopg2`
- `pymongo`
- `pandas`

## Installation:

```bash
pip install google-api-python-client
pip install streamlit
pip install psycopg2
pip install pymongo
pip install pandas

```

## Features:

The YouTube Data Harvesting and Warehousing application offers the following functions:

- Retrieval of channel and video data from YouTube using the YouTube API.
- Storage of data in a MongoDB database as a data lake.
- Migration of data from the data lake to a SQL database for efficient querying and analysis.
- Search and retrieval of data from the SQL database using different search options.

For a Python code implementation, consider the following code snippets for each feature. Please note that these are simplified examples, and actual implementation may require additional considerations based on the specific project requirements and architecture.

