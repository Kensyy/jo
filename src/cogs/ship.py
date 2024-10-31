import discord
import random
import io
from discord import app_commands
from discord.ext import commands
from PIL import Image, ImageFont, ImageDraw

class ShipCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='ship', description='Cheque se alguém é sua alma gêmea')
    @app_commands.describe(usuario1="Primeiro usuário a shippar", usuario2="Segundo usuário a shippar")
    async def ship(self, interaction: discord.Interaction, usuario1: discord.User, usuario2: discord.User):
        porcentagem = random.randint(0,100)
        metade1 = usuario1.name[:len(usuario1.name)//2]
        metade2 = usuario2.name[len(usuario2.name)//2:]
        nomeship = metade1 + metade2

        imagem1 = await usuario1.avatar.read()
        avatar1 = Image.open(io.BytesIO(imagem1))
        avatar1 = avatar1.resize((250,250))

        imagem2 = await usuario2.avatar.read()
        avatar2 = Image.open(io.BytesIO(imagem2))
        avatar2 = avatar2.resize((250,250))

        planodefundo = Image.new("RGB",(500,280),(56,56,56))
        planodefundo.paste(avatar1,(0,0))
        planodefundo.paste(avatar2,(250,0))

        fundodraw = ImageDraw.Draw(planodefundo)
        fundodraw.rounded_rectangle(((0,250),(500*(porcentagem/100),289)),fill=(207, 13, 48),radius=5)

        fonte = ImageFont.truetype("RobotoMono-Bold.ttf",20)
        fundodraw.text((230,250),f"{porcentagem}%",font=fonte)

        buffer = io.BytesIO()
        planodefundo.save(buffer,format="PNG")
        buffer.seek(0)

        if porcentagem <= 35:
            mensagem_extra = "😅 Vish amigos, se pá é melhor ficar sozinho viu...?"
        elif porcentagem > 35 and porcentagem <= 65:
            mensagem_extra = "☺️ Até vai, só não seguir o exemplo do Chico Moedas"
        elif porcentagem > 65:
            mensagem_extra = "😍 Ai sim! Quando vai ser o casamento?"


        await interaction.response.send_message(f"**Será que vamos ter um casal novo por aqui?**\n {usuario1.mention} + {usuario2.mention} = ✨ `{nomeship}` ✨\n{mensagem_extra}",file=discord.File(fp=buffer,filename="file.png"))

async def setup(bot):
    await bot.add_cog(ShipCommand(bot))