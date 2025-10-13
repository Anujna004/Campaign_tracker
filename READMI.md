# Campaign Tracker Web App

## Campaign Tracker is a web application to efficiently manage marketing campaigns.
 - It allows users to:

 - Add, update, and delete campaigns

- Track campaign status (Active, Paused, Completed)

- Search campaigns dynamically

- View dashboard summary with total and status-wise counts

**Frontend:** HTML, CSS, JavaScript
**backend:** Flask + MongoDB for the backend.

---
## Features

-Login / Logout system with validation

-**Dashboard Summary:** Total campaigns and status-wise counts

-**Add Campaign:** Name, client, start date, and status selection

-**Edit Status:** Change status using colored dropdown

-**Search Campaigns:** Real-time filtering

-**Delete Campaign:** Confirmation modal before deletion

-**Success Modal:** Confirmation for campaign addition

---
## Backend Setup
### 1. Navigate to backend folder :
cd backend
### 2. Install dependencies: 
pip install -r requirements.txt

### 3. Run the Flask Server:
python app.py
  
Backend API will be available at: http://localhost:5000/api


## Frontend Setup
1. Navigate to the frontend/ folder.

2. Open **index.html** in a browser

3. Login with 

   **Username:** admin
   **Password:** 1234

Start adding and managing Campaigns