import asyncio
import anthropic
import discord

from pocketbase import PocketBase
from anthropic import Client as Claude
from discord import Client as Snap

# env_loader.py
import os
from dotenv import load_dotenv

def load_env_vars():
    load_dotenv()
    webhook_url = os.getenv("WEBHOOK_URL")
    discord_token = os.getenv("DISCORD_API_KEY")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    pocketbase_url = os.getenv("POCKETBASE_URL")
    pocketbase_email = os.getenv("POCKETBASE_EMAIL")
    pocketbase_password = os.getenv("POCKETBASE_PASSWORD")

    return {
        "webhook_url": webhook_url,
        "discord_token": discord_token,
        "anthropic_api_key": anthropic_api_key,
        "pocketbase_url": pocketbase_url,
        "pocketbase_email": pocketbase_email,
        "pocketbase_password": pocketbase_password,
    }

env_vars = load_env_vars()

# Initialize Discord, Pocketbase, and Anthropic clients
discord_client = Snap(intents=discord.Intents.all())
anthropic_client = Claude(api_key=env_vars["anthropic_api_key"])
pb = PocketBase(env_vars["pocketbase_url"])
pb_auth_data = pb.admins.auth_with_password(env_vars["pocketbase_email"], env_vars["pocketbase_password"])

# Initialize PocketBase collection
game_info = pb.collection("game")
npc_collection = pb.collection("npcs")

id = "2u7dofvuxcp3s2n"
npc_info = npc_collection.get_one(id)

print(npc_info.name])