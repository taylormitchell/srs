import sqlite3

conn = sqlite3.connect('srs.db')
conn.execute("PRAGMA foreign_keys=ON;")
c = conn.cursor()

c.execute('''
    CREATE TABLE CONCEPTS(
        cid integer primary key autoincrement, 
        created_date int DEFAULT (cast(strftime('%s','now') as int)), 
        interval INT DEFAULT 0,
        last_review int DEFAULT 0,
        due_date int DEFAULT (cast(strftime('%s','now') as int))
    )
    ''')

c.execute('''
    CREATE TABLE QUESTIONS(
        qid integer primary key autoincrement, 
        created_date int DEFAULT (cast(strftime('%s','now') as int)),
        cid integer,
        front text,
        back text,
        num_reviews int default  0,
        last_review int DEFAULT 0,
        foreign key(cid) references concepts(cid)
    )
    ''')

c.execute('''
    CREATE TABLE REVIEWS(
        rid integer primary key autoincrement, 
        qid integer,
        cid integer,
        start_time real,
        end_time real,
        elapsed_time real,
        passed integer,
        foreign key(cid) references concepts(cid),
        foreign key(qid) references questions(qid)
    )
    ''')

q = """
create trigger update_question_after_review
    after insert on reviews
begin
    update questions
    set 
        num_reviews = num_reviews + 1,
        last_review = new.end_time
    where qid = new.qid;
end;
"""
c.execute(q)

q = """
create trigger update_concepts_after_review
    after insert on reviews
begin
    update concepts 
    set last_review = new.end_time,
        interval = case
            when new.passed = 0 then 0
            else 2*interval + 1
        END
    where cid = new.cid;

    update concepts 
    set due_date = (cast(strftime('%s','now') as int)) + (24*60*60*interval)
    where cid = new.cid;
end;
"""
c.execute(q)

conn.commit()
conn.close()