import asyncio
import anthropic
import discord
import time
import random

from pocketbase import PocketBase
from anthropic import Client as Claude
from discord import Client as Snap

# env_loader.py
import os
from dotenv import load_dotenv

response_queue = []

async def gather_instances():
  global response_queue
  global user_input

  user_input =""
  
  instances = [
      instance("kirkgq1udfwzqhv", "lddbtbyby25zknp", response_queue, user_input),
      # instance("2u7dofvuxcp3s2n", response_queue),
      # instance("rmnr73yi8qw6w5p", response_queue)
  ]
  
  await asyncio.gather(game_clock(), main(), *[await inst(npc_id, game_id, response_queue, user_input) for inst in instances])  
  
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
game_collection = pb.collection("game")
npc_collection = pb.collection("npcs")

class Intellegence:
  MODELS = {
      "haiku": "claude-3-haiku-20240307",
      "sonnet": "claude-3-sonnet-20240229",
      "opus": "claude-3-opus-20240229"
  }

  def __init__(self, message_bank, model_name="sonnet", max_tokens=1024, temperature=1, system_message="You are a helpful assistant."):
    self.message_bank = message_bank
    self.model = self.MODELS[model_name]
    self.max_tokens = max_tokens
    self.temperature = temperature
    self.system_message = system_message

  def add_user_message(self, message_content):
    self.message_bank.append({"role": "user", "content": message_content})

  def add_assistant_message(self, message_content):
    self.message_bank.append({"role": "assistant", "content": message_content})

  def set_system_message(self, message_content):
    self.system_message = message_content

  def post_messages(self):
    response = anthropic_client.messages.create(
        model=self.model,
        max_tokens=self.max_tokens,
        temperature=self.temperature,
        system=self.system_message,
        messages=self.message_bank
    )
    self.add_assistant_message(response.content[0].text)

async def game_clock():
  global game_clock
  global game_time

  game_time = {
    'hour': 0,
    'minute': 0
  }

  game_clock = "00:00"
  
  while True:
    await asyncio.sleep(0.5)
    i += 1
    game_time['minute'] += 1

    if game_time['minute'] == 60:
      game_time['hour'] += 1
      game_time['minute'] = 0

    if game_time['hour'] == 24:
      game_time['hour'] = 0

    # Use zero-padding and format the clock
    game_clock = "{:02d}:{:02d}".format(game_time['hour'], game_time['minute'])

async def main():
  while True:
    print(game_clock)
    user_input_basis = await asyncio.get_running_loop().run_in_executor(None, get_user_input)

    if user_input_basis == "...":
      pass

    else: 
      user_input = user_input_basis

    for i, response in enumerate(response_queue):
      print(response)
      response_queue.pop(i)

def get_user_input():
  try:
      user_input = input("User: ")
  except (KeyboardInterrupt, EOFError):
      user_input = None
  return user_input

async def instance(npc_id, game_id, response_queue, user_input):
  user_input = user_input
  
  npc_info = npc_collection.get_one(npc_id)
  npc_lore_dict = npc_info.lore
  npc_memories = npc_info.memory
  npc_conversation_history = npc_info.conversation
  npc_username = npc_info.username
  
  game_info = game_collection.get_one(game_id)
  game_master_prompt = game_info.master_prompt
  game_current_nations = game_info.current_nations
  
  npc_description = npc_lore_dict["description"]
  npc_characteristics = npc_lore_dict["characteristics"]
  
  
  npc = Intellegence(npc_conversation_history)
  
  system_message = (
    f"""
      <character>
        You are {npc_description['full_name']}, the {npc_description['occupation']} of {npc_description['nationality']}, a fictitious {npc_description['politics']} in a multiplayer nation-building role-playing game.
        As {npc_characteristics['short_name']}, you value {npc_characteristics['values']}. You also {npc_characteristics['Personality']}.
      </character>
      <game_info>
        {game_master_prompt}
        {game_current_nations}
      </game_info>
      <memories>
        {npc_memories}
      </memories>
        {npc_conversation_history}
      </memories>
    """
  )
  
  npc.set_system_message(system_message)
  npc.add_user_message(f"[{game_clock}] System: You have connected to the diplomatic chatroom.")
  npc.post_messages()

  npc_response = npc.message_bank[-1]["content"]

  response_queue.append(f"[{game_clock}] {npc_username}: {npc_response}")

  while True:
    last_message = user_input
    current_game_time = game_time
    target_game_time = {
      'hour': game_time["hour"],
      'minute': game_time["minute"] + 5
    }
    
    while game_time != target_game_time:
      await asyncio.sleep(0.5)
    
    if user_input == last_message:
      npc.add_user_message(f"[{game_clock}] System: No New Messages")

    else:
      npc.add_user_message(f"[{game_clock}] Stranger: {user_input}")

    npc.post_messages()
    pb.collection('npcs').update(npc_id, {"conversation": npc_conversation_history})

asyncio.run(gather_instances())

