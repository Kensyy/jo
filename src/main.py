import discord
import os
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# verifica toda a pasta pra ver quais os arquivos que tem que carregar pros comandos
async def load_cogs():
    for filename in os.listdir('src/cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f"Cog {filename} carregada com sucesso.")
            except Exception as e:
                print(f"Erro ao carregar {filename}: {e}")

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.CustomActivity(name="👉 Servidor oficial | https://bit.ly/o-culto-discord"))
    try:
        bot.tree.clear_commands(guild=discord.Object(id=1044018298951569498))
        await bot.tree.sync(guild=discord.Object(id=1044018298951569498))
        
    except Exception as e:
        print(f"Erro ao sincronizar slash commands: {e}")
    print(f"A {bot.user.name} está online!")

async def main():
    await load_cogs()
    await bot.start(DISCORD_BOT_TOKEN)
    
@bot.tree.command(name="ping", description="Testa o bot")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")


import asyncio
asyncio.run(main())
