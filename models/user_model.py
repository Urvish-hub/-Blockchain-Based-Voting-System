import mysql.connector
from config import DB_CONFIG
from werkzeug.security import generate_password_hash, check_password_hash

class UserModel:
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
    def register_user(username, email, password, full_name):
        """Register a new voter"""
        conn = UserModel.get_connection()
        if not conn:
            return False, "Database connection failed"
        
        try:
            cursor = conn.cursor()
            # Check if username or email already exists
            cursor.execute("SELECT id FROM voters WHERE username = %s OR email = %s", (username, email))
            if cursor.fetchone():
                return False, "Username or email already exists"
            
            # Hash password
            hashed_password = generate_password_hash(password)
            
            # Insert new voter
            cursor.execute(
                "INSERT INTO voters (username, email, password, full_name) VALUES (%s, %s, %s, %s)",
                (username, email, hashed_password, full_name)
            )
            conn.commit()
            return True, "Registration successful"
        except mysql.connector.Error as e:
            return False, f"Registration failed: {str(e)}"
        finally:
            if conn:
                conn.close()

    @staticmethod
    def authenticate_user(username, password):
        """Authenticate voter login"""
        conn = UserModel.get_connection()
        if not conn:
            return None, "Database connection failed"
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM voters WHERE username = %s", (username,))
            user = cursor.fetchone()
            
            if user and check_password_hash(user['password'], password):
                return user, "Login successful"
            return None, "Invalid username or password"
        except mysql.connector.Error as e:
            return None, f"Authentication error: {str(e)}"
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        conn = UserModel.get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, username, email, full_name, has_voted FROM voters WHERE id = %s", (user_id,))
            return cursor.fetchone()
        except mysql.connector.Error as e:
            print(f"Error fetching user: {e}")
            return None
        finally:
            if conn:
                conn.close()

    @staticmethod
    def has_user_voted(user_id):
        """Check if user has already voted"""
        conn = UserModel.get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT has_voted FROM voters WHERE id = %s", (user_id,))
            result = cursor.fetchone()
            return result[0] if result else False
        except mysql.connector.Error as e:
            print(f"Error checking vote status: {e}")
            return False
        finally:
            if conn:
                conn.close()

    @staticmethod
    def mark_user_as_voted(user_id):
        """Mark user as having voted"""
        conn = UserModel.get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE voters SET has_voted = TRUE WHERE id = %s", (user_id,))
            conn.commit()
            return True
        except mysql.connector.Error as e:
            print(f"Error updating vote status: {e}")
            return False
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_all_voters():
        """Get all registered voters (for admin)"""
        conn = UserModel.get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, username, email, full_name, has_voted, created_at FROM voters ORDER BY created_at DESC")
            return cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Error fetching voters: {e}")
            return []
        finally:
            if conn:
                conn.close()

    @staticmethod
    def update_profile(user_id, full_name, email):
        """Update user profile"""
        conn = UserModel.get_connection()
        if not conn:
            return False, "Database connection failed"
        
        try:
            cursor = conn.cursor()
            # Check if email is already taken by another user
            cursor.execute("SELECT id FROM voters WHERE email = %s AND id != %s", (email, user_id))
            if cursor.fetchone():
                return False, "Email already exists"
            
            # Update profile
            cursor.execute(
                "UPDATE voters SET full_name = %s, email = %s WHERE id = %s",
                (full_name, email, user_id)
            )
            conn.commit()
            return True, "Profile updated successfully"
        except mysql.connector.Error as e:
            return False, f"Failed to update profile: {str(e)}"
        finally:
            if conn:
                conn.close()

    @staticmethod
    def change_password(user_id, old_password, new_password):
        """Change user password"""
        conn = UserModel.get_connection()
        if not conn:
            return False, "Database connection failed"
        
        try:
            cursor = conn.cursor(dictionary=True)
            # Get current password
            cursor.execute("SELECT password FROM voters WHERE id = %s", (user_id,))
            result = cursor.fetchone()
            
            if not result or not check_password_hash(result['password'], old_password):
                return False, "Current password is incorrect"
            
            # Update password
            hashed_password = generate_password_hash(new_password)
            cursor.execute(
                "UPDATE voters SET password = %s WHERE id = %s",
                (hashed_password, user_id)
            )
            conn.commit()
            return True, "Password changed successfully"
        except mysql.connector.Error as e:
            return False, f"Failed to change password: {str(e)}"
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_vote_history(user_id):
        """Get vote history for a user"""
        conn = UserModel.get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT 
                    v.id as vote_id,
                    v.voted_at,
                    c.name as candidate_name,
                    c.party,
                    c.position
                FROM votes v
                INNER JOIN candidates c ON v.candidate_id = c.id
                WHERE v.voter_id = %s
                ORDER BY v.voted_at DESC
            """, (user_id,))
            return cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Error fetching vote history: {e}")
            return []
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_user_statistics(user_id):
        """Get user statistics"""
        conn = UserModel.get_connection()
        if not conn:
            return {}
        
        try:
            cursor = conn.cursor(dictionary=True)
            # Get total votes cast by user
            cursor.execute("SELECT COUNT(*) as total_votes FROM votes WHERE voter_id = %s", (user_id,))
            vote_count = cursor.fetchone()
            
            # Get account creation date
            cursor.execute("SELECT created_at FROM voters WHERE id = %s", (user_id,))
            account_info = cursor.fetchone()
            
            return {
                'total_votes': vote_count['total_votes'] if vote_count else 0,
                'account_created': account_info['created_at'] if account_info else None
            }
        except mysql.connector.Error as e:
            print(f"Error fetching user statistics: {e}")
            return {}
        finally:
            if conn:
                conn.close()

