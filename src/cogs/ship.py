import discord
import random
import io
from discord import app_commands
from discord.ext import commands
from PIL import Image, ImageFont, ImageDraw
import json

class ShipCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Carregar as mensagens do JSON
        with open('utils\ship_messages.json', 'r', encoding='utf-8') as f:
            self.mensagens = json.load(f)["mensagens"]

    @app_commands.command(name='ship', description='Cheque se alguém é sua alma gêmea')
    @app_commands.describe(usuario1="Primeiro usuário a shippar", usuario2="Segundo usuário a shippar")
    async def ship(self, interaction: discord.Interaction, usuario1: discord.User, usuario2: discord.User):
        porcentagem = random.randint(0, 100)
        metade1 = usuario1.name[:len(usuario1.name)//2]
        metade2 = usuario2.name[len(usuario2.name)//2:]
        nomeship = metade1 + metade2

        imagem1 = await usuario1.avatar.read()
        avatar1 = Image.open(io.BytesIO(imagem1))
        avatar1 = avatar1.resize((250, 250))

        imagem2 = await usuario2.avatar.read()
        avatar2 = Image.open(io.BytesIO(imagem2))
        avatar2 = avatar2.resize((250, 250))

        planodefundo = Image.new("RGB", (500, 280), (56, 56, 56))
        planodefundo.paste(avatar1, (0, 0))
        planodefundo.paste(avatar2, (250, 0))

        fundodraw = ImageDraw.Draw(planodefundo)
        fundodraw.rounded_rectangle(((0, 250), (500 * (porcentagem / 100), 289)), fill=(207, 13, 48), radius=5)

        fonte = ImageFont.truetype("utils\RobotoMono-Bold.ttf", 20)
        fundodraw.text((230, 250), f"{porcentagem}%", font=fonte)

        buffer = io.BytesIO()
        planodefundo.save(buffer, format="PNG")
        buffer.seek(0)

        # Selecionar a mensagem apropriada com base na porcentagem
        if porcentagem <= 35:
            mensagem_extra = random.choice(self.mensagens["baixo"])
        elif 35 < porcentagem <= 65:
            mensagem_extra = random.choice(self.mensagens["medio"])
        else:
            mensagem_extra = random.choice(self.mensagens["alto"])

        await interaction.response.send_message(
            f"**Será que vamos ter um casal novo por aqui?**\n {usuario1.mention} + {usuario2.mention} = ✨ `{nomeship}` ✨\n{mensagem_extra}",
            file=discord.File(fp=buffer, filename="file.png")
        )

async def setup(bot):
    await bot.add_cog(ShipCommand(bot))
