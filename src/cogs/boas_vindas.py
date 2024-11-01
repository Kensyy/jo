import discord
from discord.ext import commands

class BoasVindas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Cog BoasVindas carregada!")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = self.bot.get_channel(channel_id)
        print(f'{member} entrou no servidor')
        
        if channel:
            await channel.send(f'Bem-vindo ao servidor, {member.mention}! Dê uma olhada nas regras e aproveite!')

# Configuração para adicionar a cog ao bot
async def setup(bot):
    await bot.add_cog(BoasVindas(bot))
