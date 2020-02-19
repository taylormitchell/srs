import sqlite3

conn = sqlite3.connect('srs.db')
c = conn.cursor()

# Add concepts
c.execute("""INSERT INTO concepts DEFAULT VALUES""")
c.execute("""INSERT INTO concepts DEFAULT VALUES""")

# Add questions
c.execute("""
    INSERT INTO questions (cid, front, back, num_reviews)
    VALUES (1, 'the front', 'the back', 0);
    """)
c.execute("""
    INSERT INTO questions (cid, front, back, num_reviews)
    VALUES (1, 'the dearre', 'the baawfeaweck', 0);
    """)
c.execute("""
    INSERT INTO questions (cid, front, back, num_reviews)
    VALUES (1, 'the ', 'the b', 0);
    """)

c.execute("""
    INSERT INTO questions (cid, front, back, num_reviews)
    VALUES (2, 'capital of france?', 'paris', 0);
    """)
c.execute("""
    INSERT INTO questions (cid, front, back, num_reviews)
    VALUES (2, 'paris is the capital of what?', 'france', 0);
    """)
c.execute("""
    INSERT INTO questions (cid, front, back, num_reviews)
    VALUES (2, "france's capital is?", 'paris', 0);
    """)

conn.commit()
conn.close()