import sqlite3

conn = sqlite3.connect("data/riftwatcher.db")
cursor = conn.cursor()

print("\n--- PLAYERS ---")
cursor.execute("SELECT * FROM players")
for row in cursor.fetchall():
    print(row)

print("\n--- MATCHES ---")
cursor.execute("SELECT * FROM matches")
for row in cursor.fetchall():
    print(row)

print("\n--- PLAYER_MATCH_STATS ---")
cursor.execute("SELECT * FROM player_match_stats")
for row in cursor.fetchall():
    print(row)

conn.close()