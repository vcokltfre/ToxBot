from asyncio import get_event_loop
from aiomysql import create_pool
from discord import Message

from config.config import dbcreds as creds

CREATE = """
CREATE TABLE IF NOT EXISTS Infractions(
    id              BIGINT NOT NULL AUTO_INCREMENT,
    user_id         BIGINT NOT NULL,
    guild_id        BIGINT NOT NULL,
    message_id      BIGINT NOT NULL,
    message         VARCHAR(2000) NOT NULL,
    toxic           FLOAT NOT NULL,
    severe_toxic    FLOAT NOT NULL,
    obscene         FLOAT NOT NULL,
    threat          FLOAT NOT NULL,
    insult          FLOAT NOT NULL,
    identity_hate   FLOAT NOT NULL,
    date            DATE DEFAULT NOW(),
    PRIMARY KEY (id),
    UNIQUE KEY (user_id, message_id)
);
"""

CREATE_INFRACTION = """
INSERT INTO Infractions
(user_id, guild_id, message_id, message, toxic, severe_toxic, obscene, threat, insult, identity_hate)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""

GET_INFRACTION_BY_MID = "SELECT (id) FROM Infractions WHERE message_id = %s;"

GET_USER_INFRACTIONS = """
SELECT * FROM Infractions
WHERE user_id = %s and guild_id = %s;
"""


class Database:
    def __init__(self, bot):
        self.pool = None
        self.bot = bot

    async def init(self):
        self.pool = await create_pool(**creds, loop=get_event_loop())

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(CREATE)

    async def create_infraction(self, message: Message, results: dict):
        async with self.pool.acquire() as conn:
            await conn.begin()
            async with conn.cursor() as cur:
                await cur.execute(CREATE_INFRACTION, (message.author.id, message.guild.id, message.id, message.content,
                    results["toxic"], results["severe_toxic"], results["obscene"], results["threat"], results["insult"], results["identity_hate"],
                ))
                await cur.execute(GET_INFRACTION_BY_MID, (message.id,))
                data = await cur.fetchone()
            await conn.commit()
            self.bot.logger.info(f"Created infraction: {data}")
            return data[0]

    async def get_infractions_for(self, userid: int, guildid: int):
        async with self.pool.acquire() as conn:
            await conn.begin()
            async with conn.cursor() as cur:
                await cur.execute(GET_USER_INFRACTIONS, (userid, guildid))
                data = await cur.fetchall()
            await conn.commit()
            return data

    async def get_infraction(self, infractionid: int, guildid: int):
        async with self.pool.acquire() as conn:
            await conn.begin()
            async with conn.cursor() as cur:
                await cur.execute("SELECT * FROM Infractions WHERE id = %s and guild_id = %s;", (infractionid, guildid))
                data = await cur.fetchone()
            await conn.commit()
            return data
