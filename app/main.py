"""
Cleaning database from garbage urls
"""
import asyncio
from typing import Dict, List

from db.db import Connection
from config.config import settings
import tree_processing.tree_processing as tp


async def get_urls(conn)-> Dict[str, List[str]]:
    """
    Extract urls to analysis from DB. 
    """
    # TODO: REFACTOR: If DB is large -- should be refactored as generator, extracting data by portions
    rows = await conn.db_query_select_fetch_all(f"SELECT * FROM {settings.DOMAINS_TABLE};")
    data =  {}
    for row in rows:
        if row[0] not in data:
            data[row[0]] = []
        
        data[row[0]].append(row[1])
        
    for k, v in data.items():
        data[k] = sorted(v, key = lambda x: len(x))
        
    return data


async def push_to_rules(conn, project_id, patterns):
    """insert generated rules into db"""
    # TODO: REFACTOR: do not upload rules that are already exist in the table (create unique constraint in db?)
    s = f"INSERT INTO {settings.RULES_TABLE} (project_id, regexp) VALUES (?, ?)"
    await conn.db_query_insertmany(s, [(project_id, p) for p in patterns])


async def main():
    async with Connection(settings.PATH_TO_DB) as conn:
        source_data = await get_urls(conn)
        
        # create patterns by examples
        for project_id, urls in source_data.items():
            patterns = tp.extract_patterns(urls)
            
            await push_to_rules(conn, project_id, patterns)

if __name__=="__main__":
    asyncio.run(main())