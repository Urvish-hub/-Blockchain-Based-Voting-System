import mysql.connector
from config import DB_CONFIG

class VoteModel:
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
    def cast_vote(voter_id, candidate_id):
        """Cast a vote for a candidate"""
        conn = VoteModel.get_connection()
        if not conn:
            return False, "Database connection failed"
        
        try:
            cursor = conn.cursor()
            
            # Check if user has already voted
            cursor.execute("SELECT has_voted FROM voters WHERE id = %s", (voter_id,))
            result = cursor.fetchone()
            if result and result[0]:
                return False, "You have already voted"
            
            # Insert vote record
            cursor.execute(
                "INSERT INTO votes (voter_id, candidate_id) VALUES (%s, %s)",
                (voter_id, candidate_id)
            )
            
            # Update candidate vote count
            cursor.execute(
                "UPDATE candidates SET vote_count = vote_count + 1 WHERE id = %s",
                (candidate_id,)
            )
            
            # Mark voter as having voted
            cursor.execute("UPDATE voters SET has_voted = TRUE WHERE id = %s", (voter_id,))
            
            conn.commit()
            return True, "Vote cast successfully"
        except mysql.connector.Error as e:
            conn.rollback()
            return False, f"Failed to cast vote: {str(e)}"
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_results():
        """Get election results"""
        conn = VoteModel.get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT 
                    c.id,
                    c.name,
                    c.party,
                    c.position,
                    c.bio,
                    c.image_path,
                    c.vote_count,
                    (SELECT COUNT(*) FROM votes) as total_votes
                FROM candidates c
                ORDER BY c.position, c.vote_count DESC
            """)
            return cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Error fetching results: {e}")
            return []
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_total_votes():
        """Get total number of votes cast"""
        conn = VoteModel.get_connection()
        if not conn:
            return 0
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM votes")
            result = cursor.fetchone()
            return result[0] if result else 0
        except mysql.connector.Error as e:
            print(f"Error fetching total votes: {e}")
            return 0
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_votes_by_candidate():
        """Get vote count for each candidate"""
        conn = VoteModel.get_connection()
        if not conn:
            return {}
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT 
                    c.id,
                    c.name,
                    c.vote_count
                FROM candidates c
                ORDER BY c.vote_count DESC
            """)
            results = cursor.fetchall()
            return {row['id']: row['vote_count'] for row in results}
        except mysql.connector.Error as e:
            print(f"Error fetching votes by candidate: {e}")
            return {}
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_vote_receipt(voter_id):
        """Get vote receipt details for a voter"""
        conn = VoteModel.get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT 
                    v.id as vote_id,
                    v.voted_at,
                    v.voter_id,
                    vt.username,
                    vt.full_name,
                    vt.email,
                    c.id as candidate_id,
                    c.name as candidate_name,
                    c.party,
                    c.position
                FROM votes v
                INNER JOIN voters vt ON v.voter_id = vt.id
                INNER JOIN candidates c ON v.candidate_id = c.id
                WHERE v.voter_id = %s
                ORDER BY v.voted_at DESC
                LIMIT 1
            """, (voter_id,))
            return cursor.fetchone()
        except mysql.connector.Error as e:
            print(f"Error fetching vote receipt: {e}")
            return None
        finally:
            if conn:
                conn.close()

