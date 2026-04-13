import random
import string
import time
from flask import Flask
from cassandra.cluster import Cluster
import os

app = Flask(__name__)
cassandra_host = os.getenv("CASSANDRA_HOST", "cassandra")

# Global session variable
session = None

def wait_for_cassandra():
    global session
    retry_count = 0
    while retry_count < 20:
        try:
            print(f"Forensic Lab: Attempting to connect to Cassandra at {cassandra_host} (Attempt {retry_count+1})...")
            cluster = Cluster([cassandra_host])
            temp_session = cluster.connect()
            
            temp_session.execute("""
                CREATE KEYSPACE IF NOT EXISTS forensic_lab 
                WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
            """)
            temp_session.set_keyspace('forensic_lab')
            temp_session.execute("""
                CREATE TABLE IF NOT EXISTS activity_log (
                    id uuid PRIMARY KEY, 
                    event_time timestamp, 
                    activity_type text, 
                    user_name text
                );
            """)
            
            session = temp_session
            print("Forensic Lab: Successfully connected and Schema verified!")
            return True
        except Exception as e:
            print(f"Forensic Lab: Cassandra not ready yet: {e}")
            retry_count += 1
            time.sleep(10) # Wait 10 seconds between retries
    return False

with app.app_context():
    if not wait_for_cassandra():
        print("Forensic Lab: CRITICAL FAILURE - Could not connect to Cassandra.")

@app.route('/')
def hello():
    if session:
        return f"Connected to Cassandra at {cassandra_host}! Database is ready for forensic artifacts."
    else:
        return "Connection failed: Database session not initialized.", 500

@app.route('/attack', methods=['POST'])
def attack():
    global session 
    try:
        if not session:
            return "Attack failed: Database session not initialized.", 500

        payload = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        
        for i in range(100):
            session.execute(
                "INSERT INTO activity_log (id, event_time, activity_type) VALUES (uuid(), toTimestamp(now()), %s)",
                (f"Prerit_Bhandari_Payload_{payload}_{i}",)
            )
        return "100 Dynamic Rows Inserted", 200
    except Exception as e:
        return f"Attack failed: {str(e)}", 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)