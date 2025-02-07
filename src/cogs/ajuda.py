import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
from discord import app_commands

load_dotenv()

ID_ATENDENTE = os.getenv("ID_ATENDENTE")

class Central(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class Dropdown(discord.ui.Select):
        def __init__(self):
            options = [
                discord.SelectOption(value="games", label="Jogos e Emuladores", emoji="🎮"),
                discord.SelectOption(value="softwares", label="Programas", emoji="🖥️"),
                discord.SelectOption(value="filmes", label="Filmes e Séries", emoji="🎬"),
                discord.SelectOption(value="other", label="Preciso de ajuda com outra coisa", emoji="❔")
            ]
            super().__init__(placeholder="Selecione uma opção...", min_values=1, max_values=1, options=options, custom_id="persistent_view:dropdown_help")

        async def callback(self, interaction: discord.Interaction):
            if self.values[0] == "games":
                await interaction.response.send_message("Precisa de ajuda pra instalar algum jogo? Cria um ticket que vamos tentar te ajudar!", ephemeral=True, view=Central.CreateTicket())
            elif self.values[0] == "softwares":
                await interaction.response.send_message("Quem não gosta de baixar um monte de programas só pra ver o que faz né? As vezes acontece alguns problemas, mas estamos aqui pra te ajudar, abre um ticket!", ephemeral=True, view=Central.CreateTicket())
            elif self.values[0] == "filmes":
                await interaction.response.send_message("Tendo problemas tentando assistir aquele filmezinho? Abre um ticket e nos fale o seu problema que tentaremos ajudar o mais rápido possível!", ephemeral=True, view=Central.CreateTicket())
            elif self.values[0] == "other":
                await interaction.response.send_message("Será disponibilizado um ticket para você, porém tenha em mente que podemos não saber responder a sua pergunta da maneira que você deseja.", ephemeral=True, view=Central.CreateTicket())

    class DropdownView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)
            self.add_item(Central.Dropdown())

    class CreateTicket(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=300)
            self.value = None

        @discord.ui.button(label="Abrir Ticket", style=discord.ButtonStyle.blurple, emoji="➕")
        async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
            ticket = None
            for thread in interaction.channel.threads:
                if f"{interaction.user.id}" in thread.name:
                    if thread.archived:
                        ticket = thread
                    else:
                        await interaction.response.send_message(ephemeral=True, content="Você já tem um atendimento em andamento!")
                        return

            async for thread in interaction.channel.archived_threads(private=True):
                if f"{interaction.user.id}" in thread.name:
                    if thread.archived:
                        ticket = thread
                    else:
                        await interaction.edit_original_response(content="Você já tem um atendimento em andamento!", view=None)
                        return

            if ticket is not None:
                await ticket.edit(archived=False, locked=False)
                await ticket.edit(name=f"{interaction.user.name} ({interaction.user.id})", auto_archive_duration=10080, invitable=False)
            else:
                ticket = await interaction.channel.create_thread(name=f"{interaction.user.name} ({interaction.user.id})", auto_archive_duration=10080)
                await ticket.edit(invitable=False)

            await interaction.response.send_message(ephemeral=True, content=f"Criei um ticket para você! {ticket.mention}")
            await ticket.send(f"📩  **|** {interaction.user.mention} ticket criado! Envie todas as informações possíveis sobre seu problema e aguarde até que um atendente responda.\n\nApós a sua questão ser respondida, você pode usar `/fecharticket` para encerrar o atendimento!")
            await ticket.send("<@&1131341624396488824>", delete_after=1.0)

    @app_commands.command(name='suporte-setup', description='[ADMINS] Realiza o Setup da mensagem de ajuda.')
    async def suportesetup(self, interaction: discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Painel Criado", ephemeral=True)
            embed = discord.Embed(colour=discord.Color.blurple(), title="Central de Ajuda do Culto", description="Se você está enfrentando problemas com algum dos nossos serviços...")
            embed.set_image(url="https://i.imgur.com/F9oIRQn.png")
            await interaction.channel.send(embed=embed, view=Central.DropdownView())
        else:
            await interaction.response.send_message("Você não tem permissão o suficiente para realizar este comando.", ephemeral=True)

    @app_commands.command(name="fecharticket", description='Feche um atendimento atual.')
    async def fecharticket(self, interaction: discord.Interaction):
        mod = interaction.guild.get_role(ID_ATENDENTE)
        if str(interaction.user.id) in interaction.channel.name or mod in interaction.user.roles:
            await interaction.response.send_message(f"O ticket foi arquivado por {interaction.user.mention}, obrigado por entrar em contato!")
            await interaction.channel.edit(archived=True, locked=True)
        else:
            await interaction.response.send_message("Isso não pode ser feito aqui...")

async def setup(bot: commands.Bot):
    await bot.add_cog(Central(bot))
