import discord
import requests
from discord import app_commands
from discord.ext import commands

class GameSearch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.json_urls = [
            "https://hydralinks.cloud/sources/fitgirl.json",
            "https://hydralinks.cloud/sources/onlinefix.json",
            "https://hydralinks.cloud/sources/dodi.json"
        ]
    def search_game(self, game_name):
        for url in self.json_urls:
            try:
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()

                for game_data in data.get("downloads", []):
                    title = game_data["title"]  # Mantém a formatação original
                    if game_name.lower() in title.lower():  # Comparação case-insensitive
                        print(f"Achou jogo: {title}")
                        download_link = game_data["uris"][0] if game_data.get("uris") else None
                        return title, download_link  # Retorna o título original

            except requests.exceptions.RequestException as e:
                print(f"Erro ao acessar {url}: {e}")

        return None, None

    def get_steam_image(self, game_name):
        """Busca a imagem do jogo na Steam API"""
        search_url = f"https://store.steampowered.com/api/storesearch/?term={game_name}&l=english&cc=US"
        try:
            response = requests.get(search_url)
            response.raise_for_status()
            data = response.json()

            if "items" in data and len(data["items"]) > 0:
                app_id = data["items"][0]["id"]
                print(f"Achou imagem: https://cdn.akamai.steamstatic.com/steam/apps/{app_id}/header.jpg")

                return f"https://cdn.akamai.steamstatic.com/steam/apps/{app_id}/header.jpg"

        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar imagem na Steam: {e}")

        return None

    @app_commands.command(name='game', description='Procura um jogo e retorna o link de download com imagem')
    async def game(self, interaction: discord.Interaction, game_name: str):
        if not game_name:
            await interaction.response.send_message(
                "⚠️ Por favor, informe o nome do jogo. Exemplo: `/game The Sims 2`",
                ephemeral=True
            )
            return

        await interaction.response.defer()
        title, download_link = self.search_game(game_name)
        print("passou do search_game")
        if not title or not download_link:
            await interaction.response.send_message("❌ Jogo não encontrado nos bancos de dados.")
            return

        image_url = self.get_steam_image(game_name) or "https://i.imgur.com/8bQZKus.png"  # Placeholder caso não encontre

        print("vai criar o embed")

        # Criando o embed
        embed = discord.Embed(
            title=title,
            color=discord.Color.blue(),
            description=f"**Baixar Jogo:** [Clique aqui para baixar o jogo]({download_link})"
        )
        embed.set_image(url=image_url)

        print("criou o embed")

        try:
            await interaction.followup.send(embed=embed)
            await interaction.response.send_message(embed=embed)
            await interaction.response.send(embed=embed)

        except Exception as e:
            print(f"Erro ao enviar a resposta: {e}")
        await interacton.followup.send_message("Jogo encontrado!", ephemeral=True, delete_after=2.0)

# Adiciona a Cog ao bot
async def setup(bot):
    await bot.add_cog(GameSearch(bot))