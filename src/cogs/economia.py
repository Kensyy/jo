import random
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

    @app_commands.command(name="amaldicoar", description="Amaldiçoe um membro do servidor com o poder do Celestial Ynsek para roubar almas dele.")
    @app_commands.describe(membro="Usuário que receberá a maldição")
    async def amaldicoar(self, interaction: discord.Interaction, membro: discord.User):
        image_url = "https://pa1.aminoapps.com/6587/bd57157214be76a2c814f2eeb6d8017b66cad806_hq.gif"
        try:
            user_data = self.db.users.find_one({"user_id": str(interaction.user.id)})
            target_data = self.db.users.find_one({"user_id": str(membro.id)})
            if user_data is None or target_data is None:
                await interaction.response.send_message("Um dos usuários não foi encontrado no banco de dados.", ephemeral=True)
                return

            last_curse_time = user_data.get("last_curse_time")
            if last_curse_time:
                last_curse_time = datetime.fromisoformat(last_curse_time)
                if datetime.utcnow() < last_curse_time + timedelta(hours=12):
                    await interaction.response.send_message("Você só pode amaldiçoar a cada 12 horas.", ephemeral=True)
                    return

            if target_data["saldo"] <= 0:
                await interaction.response.send_message(f"O usuário <@{membro.id}> não tem saldo para roubar.", ephemeral=True)
                return

            # Gera um número aleatório entre 1 e 30
            amount_to_steal = random.randint(1, 30)

            if target_data["saldo"] < amount_to_steal:
                amount_to_steal = target_data["saldo"]

            self.db.users.update_one(
                {"user_id": str(interaction.user.id)},
                {"$inc": {"saldo": amount_to_steal}, "$set": {"last_curse_time": datetime.utcnow().isoformat()}}
            )
            self.db.users.update_one(
                {"user_id": str(membro.id)},
                {"$inc": {"saldo": -amount_to_steal}}
            )

            if amount_to_steal == 30:
                message = f"O membro <@{interaction.user.id}> agradou o celestial Ynsek ao realizar um ritual de maldição ao membro <@{membro.id}> e foi presenteado com 30 almas do amaldiçoado."
                image_url = "https://i.pinimg.com/originals/95/db/bf/95dbbfb1553ee9a04cff20402ae86ed1.gif"
            else:
                message = f'O Membro <@{interaction.user.id}> realizou um ritual de maldição ao membro <@{membro.id}> e roubou {amount_to_steal} almas com o auxílio dos poderes do Celestial Ynsek.'
        except Exception as e:
            print(f'Erro ao realizar a parte de conexão: {e}')        
        try:
            embed = discord.Embed(
                colour=discord.Color.red(),
                title="O poder do Celestial Ynsek ressurge",
                description=message
            )

            embed.set_image(url=image_url)

            await interaction.channel.send(embed=embed)
            return
        except Exception as e:
            print(f'Erro ao realizar o embed: {e}')
                    
    @app_commands.command(name="abencoar", description="Abençoe um membro do servidor para compartilhar almas do Celestial Leirrac.")
    @app_commands.describe(membro="Usuário que receberá a benção")
    async def abencoar(self, interaction: discord.Interaction, membro: discord.User):
        image_url = "https://64.media.tumblr.com/715a9e19350966145612992438eb51fc/d0a52de489aa8949-b0/s500x750/f2a33c991f201a0b99f084c04c703e98d7d51428.gif"

        try:
                user_data = self.db.users.find_one({"user_id": str(interaction.user.id)})
                target_data = self.db.users.find_one({"user_id": str(membro.id)})

                if user_data is None or target_data is None:
                    await interaction.response.send_message("Um dos usuários não foi encontrado no banco de dados.", ephemeral=True)
                    return

                last_bless_time = user_data.get("last_bless_time")
                if last_bless_time:
                    last_bless_time = datetime.fromisoformat(last_bless_time)
                    if datetime.utcnow() < last_bless_time + timedelta(hours=12):
                        await interaction.response.send_message("Você só pode abençoar a cada 12 horas.", ephemeral=True)
                        return

                # Gera um número aleatório entre 1 e 30 para a bênção
                amount_to_bless = random.randint(1, 30)

                # Atualiza o saldo de ambos os usuários com o valor de bênção e registra o horário
                self.db.users.update_one(
                    {"user_id": str(interaction.user.id)},
                    {"$inc": {"saldo": amount_to_bless}, "$set": {"last_bless_time": datetime.utcnow().isoformat()}}
                )
                self.db.users.update_one(
                    {"user_id": str(membro.id)},
                    {"$inc": {"saldo": amount_to_bless}}
                )

                # Mensagem com resultado da bênção
                if amount_to_bless == 30:
                    message = f"O membro <@{interaction.user.id}> invocou o celestial Leirrac que o abençoou e <@{membro.id}> com 30 almas cada!"
                else:
                    message = f"O Membro <@{interaction.user.id}> abençoou o membro <@{membro.id}> com o poder do celestial Leirrac com {amount_to_bless} almas para ambos!"

        except Exception as e:
                print(f'Erro ao realizar a conexão com o banco de dados: {e}')
                return
            
        try:
            embed = discord.Embed(
                colour=discord.Color.green(),
                title="O poder do Celestial Leirrac abençoa",
                description=message
            )
            embed.set_image(url=image_url)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            print(f'Erro ao enviar o embed: {e}')

async def setup(bot):
    await bot.add_cog(Economia(bot))
