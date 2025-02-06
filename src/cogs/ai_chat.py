import discord
import os
from discord.ext import commands
import aiohttp

class OllamaCog(commands.Cog):
    def __init__(self, bot):
        OLLAMA_URL = os.getenv("OLLAMA_URL")
        CHANNEL_ID = os.getenv("AI_CHANNEL_ID")
        self.bot = bot
        self.ollama_url = f'{OLLAMA_URL}/api/generate'
        self.target_channel_id = CHANNEL_ID

    async def generate_ollama_response(self, prompt):
        headers = {"Content-Type": "application/json"}
        data = {
            "model": "llama3.2",
            "prompt": prompt,
        }
        print(f'Prompt enviado ao Ollama: {prompt}')
        async with aiohttp.ClientSession() as session:
            print(f'Entrou na Client Session')
            
            async with session.post(self.ollama_url, headers=headers, json=data) as response:
                print(f'Resposta: {response.status}')
                result = await response.json()
                print(result)
                
                if response.status == 200:
                    return result['choices'][0]['text']
                else:
                    return "Desculpe, não consegui obter uma resposta do Ollama."
                
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id == self.target_channel_id:
            response = await self.generate_ollama_response(message.content)
            print(response)
            await message.channel.send(response)

async def setup(bot):
    await bot.add_cog(OllamaCog(bot))
