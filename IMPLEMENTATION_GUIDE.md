# Backend Setup & Implementation Guide (VS Code + XAMPP)

Follow these steps to set up the Python Flask backend with MySQL (MariaDB) via XAMPP.

## Prerequisites
1. **XAMPP Installed**: Ensure XAMPP is installed (usually in `C:\xampp`).
2. **Python 3.10**: Ensure Python 3.10 is installed on your system.
3. **VS Code**: Have the backend folder open in VS Code.

---

## 1. Prepare MariaDB (XAMPP)
1. Open the **XAMPP Control Panel**.
2. Click **Start** for both **Apache** and **MySQL**.
3. (Optional) Click **Admin** next to MySQL to open phpMyAdmin and verify it's running.

---

## 2. VS Code Implementation Steps
1. Open the `backend` folder in VS Code.
2. Open a new Terminal in VS Code (`Ctrl + ` or Terminal > New Terminal`).
3. Create a Virtual Environment:
   ```powershell
   python -m venv venv
   ```
4. Activate the Virtual Environment:
   ```powershell
   .\venv\Scripts\activate
   ```
5. Install Dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

---

## 3. Run the Backend
Run the following command in the terminal (ensure venv is active):
```powershell
python app.py
```

### What happens automatically:
1. **Database Creation**: The script will automatically create a database named `staymatch_db` in your XAMPP MariaDB.
2. **Table Creation**: All required tables (Users, Rooms, Matches, etc.) will be created.
3. **Data Seeding**: Initial demo data (roommates, rooms, conversations) will be populated automatically so you can see results immediately.
4. **Endpoint**: The server will start at `http://0.0.0.0:5000`.

---

## 4. Connecting Android App
1. Ensure your Android Emulator can see the server. 
2. The `BASE_URL` in `RetrofitClient.kt` is set to `http://10.0.2.2:5000/api/`, which is the correct address for the emulator to reach your local machine.
3. If testing on a **physical device**, change `10.0.2.2` to your computer's local IP address.

---

## 5. Implementation Notes
- **User Models**: The backend models now match the Kotlin data classes exactly.
- **Auth**: Real JWT authentication is active. Use the Login/Signup screens in the app to create real accounts in MariaDB.
- **MariaDB**: You can view and manage your data by visiting `http://localhost/phpmyadmin/` and selecting `staymatch_db`.
