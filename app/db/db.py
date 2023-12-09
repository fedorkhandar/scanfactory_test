import aiosqlite
from typing import Tuple, List, Any

class Connection:
    def __init__(self, dbname):
        self.dbname = dbname

    async def __aenter__(self):
        self.conn = await aiosqlite.connect(self.dbname)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.conn:
            await self.conn.close()

    async def db_query_select_fetch_all(self, s: str)->List[Tuple[Any]]:
        cursor = await self.conn.cursor()
        try:
            await cursor.execute(s)
            result = await cursor.fetchall()
            if(result):
                return result
            else:
                return []
        except:
            sys.exit(1)

    async def db_query_insert(self, s: str)-> int:
        cursor = await self.conn.cursor()
        try:
            await cursor.execute(s)
            lid = cursor.lastrowid
            await self.conn.commit()
            return lid
        except sqlite3.Error as e:
            if self.conn:
                await self.conn.rollback()
            sys.exit(1)
                
    async def db_query_insertmany(self, s: str, rows: List[Any])-> None:
        cursor = await self.conn.cursor()
        try:
            await cursor.executemany(s, rows)
            await self.conn.commit()
        except sqlite3.Error as e:
            if self.conn:
                await self.conn.rollback()
            sys.exit(1)

