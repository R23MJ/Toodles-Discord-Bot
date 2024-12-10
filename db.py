'''Database connection and table creation.'''

import databases

JUMP_DATABASE_URL = "sqlite:///jumps.db"

jumps = databases.Database(JUMP_DATABASE_URL)

async def connect_databases():
    '''Connect to all databases.'''
    await jumps.connect()

async def disconnect_databases():
    '''Disconnect from all databases.'''
    await jumps.disconnect()

async def enable_foreign_keys():
    '''Enable foreign keys for all databases.'''
    await jumps.execute("PRAGMA foreign_keys = ON;")

async def create_tables():
    '''Create all tables.'''
    await jumps.execute('''
        CREATE TABLE IF NOT EXISTS jumps (
            jump_id INTEGER PRIMARY KEY AUTOINCREMENT,
            jump_time INTEGER NOT NULL,
            message_id INTEGER UNIQUE
        )
    ''')

    await jumps.execute('''
        CREATE TABLE IF NOT EXISTS jumpers (
            jumper_id INTEGER PRIMARY KEY AUTOINCREMENT,
            display_name TEXT NOT NULL,
            torn_id INTEGER NOT NULL,
            jump_id INTEGER NOT NULL,
            order_in_jump INTEGER NOT NULL,
            FOREIGN KEY (jump_id) REFERENCES jumps(jump_id) ON DELETE CASCADE
        )
    ''')

    await enable_foreign_keys()

# Create
async def add_jump(jump_time: int):
    '''Add a jump to the database.'''
    return await jumps.execute(
        "INSERT INTO jumps (jump_time) VALUES (:jump_time)",
        {"jump_time": jump_time}
    )

async def add_jumper(jump_id: int, display_name: str, torn_id: int):
    '''Add a new jumper and set their initial order in jump.'''
    async with jumps.transaction():
        max_order = await jumps.fetch_val(
            "SELECT IFNULL(MAX(order_in_jump), 0) FROM jumpers WHERE jump_id = :jump_id",
            {"jump_id": jump_id}
        )
        await jumps.execute(
            """
            INSERT INTO jumpers (display_name, torn_id, jump_id, order_in_jump)
            VALUES (:display_name, :torn_id, :jump_id, :order_in_jump)
            """,
            {"display_name": display_name, "torn_id": torn_id, "jump_id": jump_id, "order_in_jump": max_order + 1}
        )

# Read
async def get_all_jumpers():
    '''Get all jumpers.'''
    return await jumps.fetch_all("SELECT * FROM jumpers")

async def get_all_jumps():
    '''Get all jumps.'''
    return await jumps.fetch_all("SELECT * FROM jumps")

async def get_jumpers(jump_id: int):
    '''Get all jumpers for a jump, ordered by their position.'''
    return await jumps.fetch_all(
        "SELECT * FROM jumpers WHERE jump_id = :jump_id ORDER BY order_in_jump ASC",
        {"jump_id": jump_id}
    )

async def get_jumper(torn_id : int):
    '''Get a jumper.'''
    return await jumps.fetch_one("SELECT * FROM jumpers WHERE torn_id = :torn_id",
        {"torn_id": torn_id}
    )

async def get_jump_id_from_message_id(message_id : int):
    '''Get a jump ID from a message ID.'''
    return await jumps.fetch_val("SELECT jump_id FROM jumps WHERE message_id = :message_id",
        {"message_id": message_id}
    )

async def get_jump(jump_id : int):
    '''Get a jump.'''
    return await jumps.fetch_one("SELECT * FROM jumps WHERE jump_id = :jump_id",
        {"jump_id": jump_id}
    )

# Update
async def update_jumper(jumper_id : int, display_name : str, torn_id : int, jump_id : int):
    '''Update a jumper.'''
    await jumps.execute("UPDATE jumpers SET display_name = :display_name, torn_id = :torn_id, jump_id = :jump_id WHERE jumper_id = :jumper_id",
        {"display_name": display_name, "torn_id": torn_id, "jump_id": jump_id, "jumper_id": jumper_id}
    )

async def update_jump(jump_id : int, jump_time : int, message_id : int):
    '''Update a jump.'''
    await jumps.execute("UPDATE jumps SET jump_time = :jump_time, message_id = :message_id WHERE jump_id = :jump_id",
        {"jump_time": jump_time, "message_id": message_id, "jump_id": jump_id}
    )

async def update_jump_time(jump_id : int, jump_time : int):
    '''Update a jump's time.'''
    await jumps.execute("UPDATE jumps SET jump_time = :jump_time WHERE jump_id = :jump_id",
        {"jump_time": jump_time, "jump_id": jump_id}
    )

async def update_jump_message_id(jump_id : int, message_id : int):
    '''Update a jump's message ID.'''
    await jumps.execute("UPDATE jumps SET message_id = :message_id WHERE jump_id = :jump_id",
        {"message_id": message_id, "jump_id": jump_id}
    )

async def update_order_in_jump(order: list):
    '''Update the order of all jumpers in a jump.'''
    async with jumps.transaction():
        for i, jumper_id in enumerate(order):
            await jumps.execute(
                "UPDATE jumpers SET order_in_jump = :order_in_jump WHERE jumper_id = :jumper_id",
                {"order_in_jump": i + 1, "jumper_id": jumper_id}
            )

async def update_jump_time_and_order(jump_id : int, jump_time : int, order: list):
    '''Update a jump's time and the order of all jumpers in the jump.'''
    async with jumps.transaction():
        for i, jumper_id in enumerate(order):
            await jumps.execute(
                "UPDATE jumpers SET order_in_jump = :order_in_jump WHERE jumper_id = :jumper_id",
                {"order_in_jump": i + 1, "jumper_id": jumper_id}
            )
        await jumps.execute("UPDATE jumps SET jump_time = :jump_time WHERE jump_id = :jump_id",
            {"jump_time": jump_time, "jump_id": jump_id}
        )

# Delete
async def delete_jumper_from_jump(torn_id : int, jump_id : int):
    '''Delete a jumper from a jump.'''
    await jumps.execute("DELETE FROM jumpers WHERE torn_id = :torn_id AND jump_id = :jump_id",
        {"torn_id": torn_id, "jump_id": jump_id}
    )

async def delete_jump(jump_id : int):
    '''Delete a jump.'''
    async with jumps.transaction():
        await jumps.execute("DELETE FROM jumpers WHERE jump_id = :jump_id",
            {"jump_id": jump_id}
        )
        await jumps.execute("DELETE FROM jumps WHERE jump_id = :jump_id",
            {"jump_id": jump_id}
        )
