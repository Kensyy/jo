import discord
from discord import app_commands
from discord.ext import commands
from pymongo import MongoClient
from datetime import datetime, timedelta
import os

class Economia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        client = MongoClient(os.getenv("MONGODB_TOKEN"))
        self.db = client["economia"]
        self.usuarios = self.db["users"]

    @app_commands.command(name="saldo", description="Verifique o seu saldo ou o saldo de alguém")
    async def saldo(self, interaction: discord.Interaction):
        user_data = self.usuarios.find_one({"user_id": str(interaction.user.id)})
        saldo = user_data["saldo"] if user_data else 0
        await interaction.response.send_message(f"{interaction.user.mention}, seu saldo atual é de 👻 {saldo} almas.")

    @app_commands.command(name="daily", description="Receba sua recompensa diária.")
    async def daily(self, interaction: discord.Interaction):
        user_data = self.usuarios.find_one({"user_id": str(interaction.user.id)})

        now = datetime.utcnow()
        if user_data:
            ultimo_resgate = user_data.get("ultimo_recompensa", None)
            if ultimo_resgate and now - ultimo_resgate < timedelta(days=1):
                await interaction.response.send_message("Você já resgatou sua recompensa diária. Tente novamente amanhã!")
                return
            self.usuarios.update_one({"user_id": str(interaction.user.id)}, {"$set": {"ultimo_recompensa": now}, "$inc": {"saldo": 50}})
        else:
            self.usuarios.insert_one({"user_id": str(interaction.user.id), "saldo": 50, "ultimo_recompensa": now})

        await interaction.response.send_message("Recompensa diária de 👻 50 almas recebida!")

    @app_commands.command(name="transacao", description="Envie almas para outro usuário.")
    @app_commands.describe(destinatario="Usuário que receberá as almas", quantidade="Quantidade de almas a enviar")
    async def transacao(self, interaction: discord.Interaction, destinatario: discord.User, quantidade: int):
        if quantidade <= 0:
            await interaction.response.send_message("A quantidade deve ser maior que zero.")
            return
        remetente_data = self.usuarios.find_one({"user_id": str(interaction.user.id)})
        saldo_remetente = remetente_data["saldo"] if remetente_data else 0

        if saldo_remetente < quantidade:
            await interaction.response.send_message("Saldo insuficiente para completar a transação.")
            return

        self.usuarios.update_one({"user_id": str(interaction.user.id)}, {"$inc": {"saldo": -quantidade}})
        self.usuarios.update_one({"user_id": str(destinatario.id)}, {"$inc": {"saldo": quantidade}}, upsert=True)

        await interaction.response.send_message(f"{interaction.user.mention} enviou 👻 {quantidade} almas para {destinatario.mention}.")

async def setup(bot):
    await bot.add_cog(Economia(bot))
