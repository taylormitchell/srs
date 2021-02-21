import sqlite3
import pandas as pd
from datetime import datetime

class SRS:
    def __init__(self):
        self.conn = sqlite3.connect('srs.db')
        self.c = self.conn.cursor()
        
    def add_concept(self):
        self.c.execute("INSERT INTO CONCEPTS DEFAULT VALUES")
        self.c.execute("SELECT MAX(CID) FROM CONCEPTS")
        self.conn.commit()
        new_cid = self.c.fetchone()[0]
        print(new_cid)
        
    def delete_concept(self,  cid):
        self.c.execute(f"DELETE FROM CONCEPTS WHERE cid = {cid}")
        
    def add_question(self, cid, front, back):
        self.c.execute(f"""
        INSERT INTO questions (cid, front, back)
        VALUES ({cid}, '{front}', '{back}');
        """)
        self.conn.commit()
        
    def show_db(self, table_names=None):
        if table_names is None: table_names = self._get_names()
        for table_name in table_names:
            print(table_name)
            q = f"select * from {table_name}"
            df = pd.read_sql(q, self.conn)
            for col in df.columns[df.columns.str.contains('_(date|time)')]:
                df[col] = pd.to_datetime(df[col], unit='s')
            display(df)
            
    def start_session(self, date):
        questions = self._get_due_questions(date)
        return Session(questions, self)      
    
    def close(self):
        self.conn.close()
        
    def _add_review(self, qid, cid, start_time, end_time, elapsed, passed):
        self.c.execute(f"""
        INSERT INTO REVIEWS (qid, cid, start_time, end_time, elapsed, passed)
        VALUES ({qid}, {cid}, {start_time}, {end_time}, {elapsed}, {passed});
        """)
        self.conn.commit()
           
    def _get_due_questions(self, date):
        q = f"""
        select q.qid, q.cid, q.front, q.back
        -- 1) select questions whose concept is due
        from (
            select q.*
            from questions q, concepts c
            where q.cid = c.cid and c.due_date <= '{date}'
        ) q
        -- 2) select questions with the fewest reviews
        join (
            select cid, min(num_reviews) num_rev
            from questions
            group by cid
        ) min
        on 
            q.num_reviews = min.num_rev 
            and q.cid = min.cid
        -- 3) randomly select 1 question from each concept
        group by q.cid
        having min(random())
        """
        # pd.read_sql(q, conn)
        self.c.execute(q)
        records = self.c.fetchall()
        return [Question(*r) for r in records]

        
    def _get_names(self, type='table'):
        q = f"""
        select name from sqlite_master 
        where type = '{type}' and tbl_name != 'sqlite_sequence'
        """
        self.c.execute(q)
        names = [o[0] for o in self.c.fetchall()]
        return names
    
class Question:
    def __init__(self, qid, cid, front, back, 
                 start_time=None, end_time=None, 
                 elapsed=None, passed=None):
        self.qid = qid
        self.cid = cid
        self.front = front
        self.back = back
        self.start_time = start_time
        self.end_time = end_time
        self.elapsed = elapsed
        self.passed = passed
        
    def start(self):
        self.start_time = datetime.now().timestamp()
        return self.front
        
    def end(self):
        self.end_time = datetime.now().timestamp()
        self.elapsed = self.end_time - self.start_time
        return self.back
        
    def yes(self): 
        self.passed = 1
        
    def no(self): 
        self.passed = 0
        
    def dump(self):
        vs = ['qid','cid','start_time','end_time','elapsed','passed']
        return {k:getattr(self,k) for k in vs}

class Session:
    def __init__(self, questions, srs, push_dist=5):
        self.srs = srs
        self.questions = questions
        self.push_dist = push_dist
        
    def next(self):
        front = self.questions[0].start()
        print(front)
        
    def end(self):
        back = self.questions[0].end()
        print(back)
        print('\nDid you get it?')
        
    def yes(self):
        self.questions[0].yes()
        self.srs._add_review(**self.questions[0].dump())
        del self.questions[0]
            
    def no(self):
        self.questions[0].no()
        self.srs._add_review(**self.questions[0].dump())
        # Move the question back into the queue
        i = min(len(self.questions)-1, self.push_dist)    
        self.questions.insert(i, self.questions.pop(0))
            