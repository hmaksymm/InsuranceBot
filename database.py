import sqlalchemy
from databases import Database
from sqlalchemy import MetaData, Table, Column, Integer, String, Text, select, insert, update, JSON

class ChatHistoryDB:
    def __init__(self, database_url="sqlite:///./chat_history.db"):
        self.database_url = database_url
        self.metadata = MetaData()
        self.chat_histories = Table(
            "chat_histories",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("chat_id", String, unique=True, index=True),
            Column("chat_history", Text, default=""),
            Column("step_passed", Integer, nullable=True),
            Column("passport_data", JSON, nullable=True),
            Column("vehicle_data", JSON, nullable=True)
        )
        self.database = Database(self.database_url)
        self.engine = sqlalchemy.create_engine(self.database_url)
        self.metadata.create_all(self.engine)

    async def connect(self):
        await self.database.connect()

    async def disconnect(self):
        await self.database.disconnect()

    
    
    async def get_trimmed_chat_history(self, chat_id: str, max_length: int = 2048) -> str:
        history = await self.get_chat_history(chat_id)
        entries = history.strip().split("\n")
        entries = [line for line in entries if line]

        pairs = []
        i = 0
        while i < len(entries) - 1:
            if entries[i].startswith("User:") and entries[i + 1].startswith("Bot:"):
                pairs.append(f"{entries[i]}\n{entries[i+1]}\n")
                i += 2
            else:
                i += 1

        trimmed_history = ""
        current_length = 0

        for entry in reversed(pairs):
            entry_length = len(entry)
            if current_length + entry_length > max_length:
                break
            trimmed_history = entry + trimmed_history
            current_length += entry_length

        return trimmed_history

    
    
    async def get_chat_history(self, chat_id: str) -> str:
        query = select(self.chat_histories.c.chat_history).where(self.chat_histories.c.chat_id == chat_id)
        result = await self.database.fetch_one(query)
        return result[0] if result else ""

    async def add_message(self, chat_id: str, user_message: str, bot_response: str):
        existing_history = await self.get_chat_history(chat_id)
        new_entry = f"User: {user_message}\nBot: {bot_response}\n"
        updated_history = existing_history + new_entry

        query_check = select(self.chat_histories.c.id).where(self.chat_histories.c.chat_id == chat_id)
        exists = await self.database.fetch_one(query_check)

        if exists:
            query_update = (
                update(self.chat_histories)
                .where(self.chat_histories.c.chat_id == chat_id)
                .values(chat_history=updated_history)
            )
            await self.database.execute(query_update)
        else:
            query_insert = insert(self.chat_histories).values(
                chat_id=chat_id,
                chat_history=new_entry,
                step_passed=1,
                passport_data={},
                vehicle_data={}
            )
            await self.database.execute(query_insert)

    async def get_data_confirmed(self, chat_id: str):
        query = select(self.chat_histories.c.data_confirmed).where(self.chat_histories.c.chat_id == chat_id)
        result = await self.database.fetch_one(query)
        return result[0] if result else None

    async def set_data_confirmed(self, chat_id: str, data: str):
        query = (
            update(self.chat_histories)
            .where(self.chat_histories.c.chat_id == chat_id)
            .values(data_confirmed=data)
        )
        await self.database.execute(query)

    async def get_step_passed(self, chat_id: str):
        query = select(self.chat_histories.c.step_passed).where(self.chat_histories.c.chat_id == chat_id)
        result = await self.database.fetch_one(query)
        return result[0] or 0 if result else 0


    async def set_step_passed(self, chat_id: str, step: int):
        query = (
            update(self.chat_histories)
            .where(self.chat_histories.c.chat_id == chat_id)
            .values(step_passed=step)
        )
        await self.database.execute(query)

    async def set_document_data(self, chat_id: str, doc_type: str, data: dict):
        column = "passport_data" if doc_type == "passport" else "vehicle_data"
        query = (
            update(self.chat_histories)
            .where(self.chat_histories.c.chat_id == chat_id)
            .values(**{column: data})
        )
        await self.database.execute(query)

    async def get_document_data(self, chat_id: str, doc_type: str) -> dict:
        column = "passport_data" if doc_type == "passport" else "vehicle_data"
        query = select(getattr(self.chat_histories.c, column)).where(self.chat_histories.c.chat_id == chat_id)
        result = await self.database.fetch_one(query)
        return result[0] if result else {}
