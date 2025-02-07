# src/cogs/anuncio.py

import discord
from discord.ext import commands
from discord import app_commands

class Anuncio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
 
    @app_commands.command(name='anuncio', description='[ADMINS] Realize um anúncio pela Jo.')
    @app_commands.describe(
        titulo="Título do anúncio",
        descricao="Descrição do anúncio",
        imagem="Url de uma imagem para servir como thumb do anúncio"
    )
    async def anuncio(self, interaction: discord.Interaction, titulo: str, descricao: str, imagem: str):
        if interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                colour=discord.Color.blurple(),
                title=titulo,
                description=descricao
            )
            if imagem.startswith("http"):
                embed.set_image(url=imagem)

            await interaction.channel.send(embed=embed)
            await interaction.channel.send("<@everyone>", delete_after=5.0)
            await interaction.response.send_message("Anúncio criado", ephemeral=True)
        else:
            await interaction.response.send_message(
                "Você não tem permissão suficiente para realizar este comando.",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Anuncio(bot))
