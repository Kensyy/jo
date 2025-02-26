import aiohttp
import asyncio
import discord
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

    async def fetch_json(self, session, url):
        try:
            async with session.get(url) as response:
                return await response.json()
        except Exception as e:
            print(f"Erro ao acessar {url}: {e}")
            return None

    async def search_game(self, game_name: str):
        """
        Percorre todos os JSONs e retorna uma lista de jogos cujo título contenha game_name.
        """
        results = []
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_json(session, url) for url in self.json_urls]
            json_datas = await asyncio.gather(*tasks)
            for data in json_datas:
                if data:
                    for game_data in data.get("downloads", []):
                        if game_name.lower() in game_data["title"].lower():
                            results.append(game_data)
                            # Aqui, mesmo que o jogo seja encontrado, continuamos
                            # armazenando os demais para permitir a navegação.
        return results

    async def get_steam_image(self, game_name: str):
        """Busca a imagem do jogo usando a API da Steam."""
        search_url = f"https://store.steampowered.com/api/storesearch/?term={game_name}&l=english&cc=US"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url) as response:
                    data = await response.json()
                    if "items" in data and data["items"]:
                        app_id = data["items"][0]["id"]
                        return f"https://cdn.akamai.steamstatic.com/steam/apps/{app_id}/header.jpg"
        except Exception as e:
            print(f"Erro ao buscar imagem na Steam: {e}")
        return None

    @app_commands.command(name='game', description='Procura um jogo e retorna o link de download')
    @app_commands.describe(game_name="Nome do Jogo a ser procurado.")
    async def game(self, interaction: discord.Interaction, game_name: str):
        if not game_name:
            await interaction.response.send_message(
                "⚠️ Por favor, informe o nome do jogo. Exemplo: `/game The Sims 2`",
                ephemeral=True
            )
            return

        await interaction.response.defer()

        results = await self.search_game(game_name)
        if not results:
            await interaction.followup.send("❌ Jogo não encontrado nos bancos de dados.")
            return

        # Exibe o primeiro resultado encontrado
        index = 0
        game_data = results[index]
        download_link = game_data["uris"][0] if game_data.get("uris") else "Link não disponível"
        image_url = await self.get_steam_image(game_name) or "https://i.imgur.com/8bQZKus.png"

        embed = discord.Embed(
            title=game_data["title"],
            description=f"🔗 Magnet Link: ```{download_link}```",
            color=discord.Color.blue()
        )
        embed.set_image(url=image_url)

        # Cria a view com o botão "Continuar busca"
        view = ContinueSearchView(results, game_name, current_index=index)
        await interaction.followup.send(embed=embed, view=view)

class ContinueSearchView(discord.ui.View):
    def __init__(self, results, game_name, current_index=0, timeout=60):
        super().__init__(timeout=timeout)
        self.results = results
        self.game_name = game_name
        self.current_index = current_index

        # Botão para continuar a busca
        self.continue_button = discord.ui.Button(label="Continuar busca", style=discord.ButtonStyle.primary)
        self.continue_button.callback = self.continue_callback

        # Se não houver mais resultados além do atual, desabilita o botão
        if len(results) <= 1:
            self.continue_button.disabled = True

        self.add_item(self.continue_button)

    async def continue_callback(self, interaction: discord.Interaction):
        self.current_index += 1
        if self.current_index >= len(self.results):
            await interaction.response.send_message("❌ Não há mais jogos correspondentes.", ephemeral=True)
            self.continue_button.disabled = True
            await interaction.message.edit(view=self)
            return

        game_data = self.results[self.current_index]
        download_link = game_data["uris"][0] if game_data.get("uris") else "Link não disponível"
        image_url = await self.get_steam_image_static(self.game_name) or "https://i.imgur.com/8bQZKus.png"

        embed = discord.Embed(
            title=game_data["title"],
            description=f"🔗 Magnet Link: ```{download_link}```",
            color=discord.Color.blue()
        )
        embed.set_image(url=image_url)

        await interaction.response.edit_message(embed=embed, view=self)

    @staticmethod
    async def get_steam_image_static(game_name: str):
        search_url = f"https://store.steampowered.com/api/storesearch/?term={game_name}&l=english&cc=US"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url) as response:
                    data = await response.json()
                    if "items" in data and data["items"]:
                        app_id = data["items"][0]["id"]
                        return f"https://cdn.akamai.steamstatic.com/steam/apps/{app_id}/header.jpg"
        except Exception as e:
            print(f"Erro ao buscar imagem na Steam: {e}")
        return None

async def setup(bot):
    await bot.add_cog(GameSearch(bot))
