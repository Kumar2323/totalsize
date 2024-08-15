from pyrogram import Client, filters
from pyrogram.types import Message
from humanize import naturalsize
from pymongo import MongoClient
import os
import asyncio
from aiohttp import web

# Pyrogram client
app = Client("my_bot",
             api_id=int(os.environ.get("API_ID")),
             api_hash=os.environ.get("API_HASH"),
             bot_token=os.environ.get("BOT_TOKEN"))

# Define a function to calculate the total size of files
def calculate_total_size(mongo_uri, db_name, collection_name):
    try:
        client_mongo = MongoClient(mongo_uri)
        db = client_mongo[db_name]
        collection = db[collection_name]
        total_size = 0
        for file in collection.find():
            if isinstance(file, dict):  # Check if file is a dictionary
                if "file_size" in file:
                    total_size += file["file_size"]
                else:
                    print(f"Warning: File {file.get('_id')} does not contain 'size' key.")
            else:
                print(f"Warning: File {file} is not a dictionary.")
        return total_size
    except Exception as e:
        print(f"Error: {e}")
        return 0

# Initialize the data variable
data = {}

# Define a command to get the total size of files
@app.on_message(filters.command("start"))
async def get_total_size(_, message: Message):
    await message.reply("Please enter the MongoDB URL, database name, and collection name separated by spaces.")
    await message.reply("Example: `mongodb+srv://user:password@cluster0.8vqs89z.mongodb.net/ db_name collection_name`")
    data[message.from_user.id] = True

# Define a handler for the MongoDB info
@app.on_message(filters.text & filters.private)
async def get_mongo_info(_, message: Message):
    if message.from_user.id in data and data[message.from_user.id]:
        mongo_info = message.text.split()
        if len(mongo_info) == 3:
            mongo_uri, db_name, collection_name = mongo_info
            total_size = calculate_total_size(mongo_uri, db_name, collection_name)
            humanized_size = naturalsize(total_size)
            await message.reply(f"The total size of files is: {humanized_size}")
            data[message.from_user.id] = False
        else:
            await message.reply("Invalid format. Please use the format: `mongodb+srv://user:password@cluster0.8vqs89z.mongodb.net/ db_name collection_name`")

async def handle(request):
    return web.Response(text="Bot is running")

async def web_server():
    web_app = web.Application()
    web_app.router.add_get("/", handle)
    return web_app

async def main():
    await app.start()

    # Start web server
    port = int(os.environ.get("PORT", 8080))
    web_app = await web_server()
    web_runner = web.AppRunner(web_app)
    await web_runner.setup()
    site = web.TCPSite(web_runner, "0.0.0.0", port)
    await site.start()

    print("Bot started")
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
