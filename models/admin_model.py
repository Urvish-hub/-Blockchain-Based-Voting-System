import mysql.connector
from config import DB_CONFIG

class AdminModel:
    @staticmethod
    def get_connection():
        """Create and return database connection"""
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            return conn
        except mysql.connector.Error as e:
            print(f"Database connection error: {e}")
            return None

    @staticmethod
    def authenticate_admin(username, password):
        """Authenticate admin login"""
        conn = AdminModel.get_connection()
        if not conn:
            return None, "Database connection failed"
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM admins WHERE username = %s", (username,))
            admin = cursor.fetchone()
            
            # For development: simple password check (NOT for production!)
            # In production, use proper password hashing
            if admin and admin['password'] == password:
                return admin, "Login successful"
            return None, "Invalid username or password"
        except mysql.connector.Error as e:
            return None, f"Authentication error: {str(e)}"
        finally:
            if conn:
                conn.close()

    @staticmethod
    def add_candidate(name, party, position, bio, image_path=None):
        """Add a new candidate"""
        conn = AdminModel.get_connection()
        if not conn:
            return False, "Database connection failed"
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO candidates (name, party, position, bio, image_path) VALUES (%s, %s, %s, %s, %s)",
                (name, party, position, bio, image_path)
            )
            conn.commit()
            return True, "Candidate added successfully"
        except mysql.connector.Error as e:
            return False, f"Failed to add candidate: {str(e)}"
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_all_candidates():
        """Get all candidates"""
        conn = AdminModel.get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM candidates ORDER BY position, vote_count DESC")
            return cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Error fetching candidates: {e}")
            return []
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_candidate_by_id(candidate_id):
        """Get candidate by ID"""
        conn = AdminModel.get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM candidates WHERE id = %s", (candidate_id,))
            return cursor.fetchone()
        except mysql.connector.Error as e:
            print(f"Error fetching candidate: {e}")
            return None
        finally:
            if conn:
                conn.close()

    @staticmethod
    def update_candidate(candidate_id, name, party, position, bio, image_path=None):
        """Update candidate information"""
        conn = AdminModel.get_connection()
        if not conn:
            return False, "Database connection failed"
        
        try:
            cursor = conn.cursor()
            if image_path:
                cursor.execute(
                    "UPDATE candidates SET name = %s, party = %s, position = %s, bio = %s, image_path = %s WHERE id = %s",
                    (name, party, position, bio, image_path, candidate_id)
                )
            else:
                cursor.execute(
                    "UPDATE candidates SET name = %s, party = %s, position = %s, bio = %s WHERE id = %s",
                    (name, party, position, bio, candidate_id)
                )
            conn.commit()
            return True, "Candidate updated successfully"
        except mysql.connector.Error as e:
            return False, f"Failed to update candidate: {str(e)}"
        finally:
            if conn:
                conn.close()

    @staticmethod
    def delete_candidate(candidate_id):
        """Delete a candidate"""
        conn = AdminModel.get_connection()
        if not conn:
            return False, "Database connection failed"
        
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM candidates WHERE id = %s", (candidate_id,))
            conn.commit()
            return True, "Candidate deleted successfully"
        except mysql.connector.Error as e:
            return False, f"Failed to delete candidate: {str(e)}"
        finally:
            if conn:
                conn.close()

