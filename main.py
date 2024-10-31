import discord
import openai
import io
from dotenv import load_dotenv
from discord import app_commands
from discord.ext import commands
from PIL import Image, ImageFont, ImageDraw, ImageOps
import random
import os

load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GUILD_ID = os.getenv("GUILD_ID")
ID_ATENDENTE = os.getenv("ID_ATENDENTE")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
# client = discord.Client(intents=intents)

bot = commands.Bot(command_prefix="!",intents=intents)

openai.api_key=OPENAI_API_KEY

# Inicialização do Bot
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.CustomActivity(name="👉 Servidor oficial | https://bit.ly/o-culto-discord"))
    # bot.tree.sync(guild=GUILD_ID)
    await bot.tree.sync()
    print(f"A {bot.user.name} está online!")
    
#region COMANDO DE SHIPPAR

@bot.tree.command(name = 'ship', description='Cheque se alguém é sua alma gêmea')
@app_commands.describe(
    usuario1 = "Primeiro usuário a shippar",
    usuario2 = "Segundo usuário a shippar",
)
async def ship(interaction: discord.Interaction,usuario1: discord.User,usuario2: discord.User):
    
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
        mensagem_extra = "😅 Não parece rolar uma química tão grande, mas quem sabe...?"
    elif porcentagem > 35 and porcentagem <= 65:
        mensagem_extra = "☺️ Essa combinação tem potencial, que tal um jantar romântico?"
    elif porcentagem > 65:
        mensagem_extra = "😍 Combinação perfeita! Quando será o casamento?"


    await interaction.response.send_message(f"**Será que vamos ter um casal novo por aqui?**\n {usuario1.mention} + {usuario2.mention} = ✨ `{nomeship}` ✨\n{mensagem_extra}",file=discord.File(fp=buffer,filename="file.png"))
#endregion COMANDO DE SHIPPAR

#region Código CHATGPT (NÃO TA FUNCIONANDO VAMOS USAR OLLAMA)

# Busca o histórico de mensagens do canal, sendo o limite 1.
# async def buscar_historico_canal(canal,limit=1):
#         messages_list = []

#         async for message in canal.history(limit=limit):
#             messages_list.append(
#                 {
#                     "role":"user" if message.author.bot!=True else "system",
#                     "content": message.content
#                 }
#             )
#         return messages_list

# # Conexão com a Open
# def ask_gpt(mensagens):
#     try:
#         response = openai.ChatCompletion.create(
#             messages=mensagens,
#             model="gpt-3.5-turbo-16k",
#             temperature=1,
#             max_tokens=500,
#         )

#         return response.choices[0].message.content
#     except:
#         return "Perdão. Ocorreu um erro, tente novamente em um minuto."

# # A cada mensagem vai realizar o processo de conexão com a open AI
# @bot.event
# async def on_message(message):
#     if message.channel.id == 1208894766511562812:
#         if message.author.bot:
#             return

#         async with message.channel.typing():
#             mensagens = await buscar_historico_canal(message.channel)
#             resposta = ask_gpt(mensagens)

#             await message.reply(resposta)
        
#             await bot.process_commands(message)
#     else:
#         return

#endregion Código ChatGPT

#region SETUP PARA SUPORTE
class Dropdown(discord.ui.Select):

  def __init__(self):
    options = [
        discord.SelectOption(value="games",
                             label="Jogos e Emuladores",
                             emoji="🎮"),
        discord.SelectOption(value="softwares", label="Programas", emoji="🖥️"),
        discord.SelectOption(value="filmes",
                             label="Filmes e Séries",
                             emoji="🎬"),
        discord.SelectOption(value="other",
                             label="Preciso de ajuda com outra coisa",
                             emoji="❔")
    ]
    super().__init__(placeholder="Selecione uma opção...",
                     min_values=1,
                     max_values=1,
                     options=options,
                     custom_id="persistent_view:dropdown_help")

  async def callback(self, interaction: discord.Interaction):
    if self.values[0] == "games":
      await interaction.response.send_message(
          "Precisa de ajuda pra instalar algum jogo? Cria um ticket que vamos tentar te ajudar!",
          ephemeral=True,
          view=CreateTicket())
    elif self.values[0] == "softwares":
      await interaction.response.send_message(
          "Quem não gosta de baixar um monte de programas só pra ver o que faz né? As vezes acontece alguns problemas, mas estamos aqui pra te ajudar, abre um ticket!",
          ephemeral=True,
          view=CreateTicket())
    elif self.values[0] == "filmes":
      await interaction.response.send_message(
          "Tendo problemas tentando assistir aquele filmezinho? Abre um ticket e nos fale o seu problema que tentaremos ajudar o mais rápido possível!",
          ephemeral=True,
          view=CreateTicket())
    elif self.values[0] == "other":
      await interaction.response.send_message(
          "Será disponibilizado um ticket para você, porém tenha em mente que podemos não saber responder a sua pergunta da maneira que você deseja.",
          ephemeral=True,
          view=CreateTicket())


class DropdownView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=None)

    self.add_item(Dropdown())


class CreateTicket(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=300)
    self.value = None

  @discord.ui.button(label="Abrir Ticket",
                     style=discord.ButtonStyle.blurple,
                     emoji="➕")
  async def confirm(self, interaction: discord.Interaction,
                    button: discord.ui.Button):
    self.value = True
    self.stop()

    ticket = None
    for thread in interaction.channel.threads:
      if f"{interaction.user.id}" in thread.name:
        if thread.archived:
          ticket = thread
        else:
          await interaction.response.send_message(
              ephemeral=True,
              content=f"Você já tem um atendimento em andamento!")
          return

    async for thread in interaction.channel.archived_threads(private=True):
      if f"{interaction.user.id}" in thread.name:
        if thread.archived:
          ticket = thread
        else:
          await interaction.edit_original_response(
              content=f"Você já tem um atendimento em andamento!", view=None)
          return

    if ticket != None:
      await ticket.edit(archived=False, locked=False)
      await ticket.edit(
          name=f"{interaction.user.name} ({interaction.user.id})",
          auto_archive_duration=10080,
          invitable=False)
    else:
      ticket = await interaction.channel.create_thread(
          name=f"{interaction.user.name} ({interaction.user.id})",
          auto_archive_duration=10080
      )  #,type=discord.ChannelType.public_thread)
      await ticket.edit(invitable=False)

    await interaction.response.send_message(
        ephemeral=True, content=f"Criei um ticket para você! {ticket.mention}")
    await ticket.send(
        f"📩  **|** {interaction.user.mention} ticket criado! Envie todas as informações possíveis sobre seu problema e aguarde até que um atendente responda.\n\nApós a sua questão ser respondida, você pode usar `/fecharticket` para encerrar o atendimento!"
    )
    await ticket.send("<@&1131341624396488824>", delete_after=1.0)
@bot.tree.command(name='suporte-setup',
            description='[ADMINS] Realiza o Setup da mensagem de ajuda.')
@app_commands.describe()
async def suportesetup(interaction: discord.Interaction):
  if interaction.user.guild_permissions.administrator:
    await interaction.response.send_message("Painel Criado", ephemeral=True)

    embed = discord.Embed(
        colour=discord.Color.blurple(),
        title="Central de Ajuda do Culto",
        description=
        "Se você está enfrentando problemas com algum dos nossos serviços, sejam eles jogos, emuladores, softwares ou filmes e séries, sinta-se livre para enviar mensagens aqui marcando os Oráculos ou o Sacerdote para lhe ajudar."
    )
    embed.set_image(url="https://i.imgur.com/F9oIRQn.png")
    await interaction.channel.send(embed=embed, view=DropdownView())
  else:
      await interaction.response.send_message("Você não tem permissão o suficiente para realizar este comando.", ephemeral=True)

@bot.tree.command(name='sugestao-setup',
              description='[ADMINS] Realiza o setup da mensagem de sugestão.')
@app_commands.describe()
async def sugestaosetup(interaction: discord.Interaction):
  if interaction.user.guild_permissions.administrator:
    await interaction.response.send_message("Painel Criado", ephemeral=True)

    embed = discord.Embed(
        colour=discord.Color.blurple(),
        title="Central de Sugestões do Culto",
        description=
        "Aqui você pode sugerir ideias de melhorias e realizar pedidos de jogos de computador (ou de emuladores), softwares, filmes e séries e sugerir ideias de eventos."
    )
    await interaction.channel.send(embed=embed)
  else:
    await interaction.response.send_message("Você não tem permissão o suficiente para realizar este comando.", ephemeral=True)

@bot.tree.command(name='enquete-setup',
              description='[ADMINS] Realiza o setup da mensagem de enquetes.')
@app_commands.describe()
async def enquetessetup(interaction: discord.Interaction):
  if interaction.user.guild_permissions.administrator:
    await interaction.response.send_message("Painel Criado", ephemeral=True)

    embed = discord.Embed(
        colour=discord.Color.blurple(),
        title="Central de Enquetes do Culto",
        description=
        "Neste canal, teremos as votações que envolvem o servidor, tais como quais tipos de evento vocês cultistas preferem entre diversas outras coisas. Por motivos específicos, vocês não poderão enviar mensagens aqui, apenas reagir as mensagens enviadas por Oráculos ou ranks superiores."
    )
    await interaction.channel.send(embed=embed)
  else:
      await interaction.response.send_message("Você não tem permissão o suficiente para realizar este comando.", ephemeral=True)

@bot.tree.command(name="fecharticket",
              description='Feche um atendimento atual.')
async def _fecharticket(interaction: discord.Interaction):
  mod = interaction.guild.get_role(ID_ATENDENTE)
  if str(interaction.user.id
         ) in interaction.channel.name or mod in interaction.author.roles:
    await interaction.response.send_message(
        f"O ticket foi arquivado por {interaction.user.mention}, obrigado por entrar em contato!"
    )
    await interaction.channel.edit(archived=True, locked=True)
  else:
    await interaction.response.send_message("Isso não pode ser feito aqui...")

@bot.tree.command(name='enquete', description='[ADMINS] Inicie uma enquete.')
@app_commands.describe(
    pergunta = "Pergunta a ser feita na enquete",
    descricao = "Descrição da pergunta",
)
async def enquete(interaction: discord.Interaction, *, pergunta: str, descricao: str, imagem: str, custom: bool):

    if interaction.user.guild_permissions.administrator:
      embed = discord.Embed(
          colour=discord.Color.blurple(),
          title= pergunta,
          description= descricao
      )
      embed.set_image(url=imagem)
      if custom == False:
          await interaction.response.send_message("Enquete criada", ephemeral=True)
          msg = await interaction.channel.send(embed=embed)
          await msg.add_reaction("👍")
          await msg.add_reaction("👎")
          await msg.add_reaction("🤷")
      else:
          msg = await interaction.channel.send(embed=embed)
    else:
      await interaction.response.send_message("Você não tem permissão o suficiente para realizar este comando.", ephemeral=True)

#endregion SETUP PARA SUPORTE

@bot.tree.command(name='anuncio', description='[ADMINS] Realize um anúncio pela Jo.')
@app_commands.describe(
    titulo = "Título do anúncio",
    descricao = "Descrição do anúncio",
    imagem = "Url de uma imagem para servir como thumb do anúncio"
)
async def enquete(interaction: discord.Interaction, *, titulo: str, descricao: str, imagem: str):

    if interaction.user.guild_permissions.administrator:
      embed = discord.Embed(
          colour=discord.Color.blurple(),
          title= titulo,
          description= descricao
      )
      if imagem.startswith("http"):
        embed.set_image(url=imagem)
      msg = await interaction.channel.send(embed=embed)
      await interaction.response.send_message("Anúncio criado", ephemeral=True)
      await interaction.channel.send("<@everyone>", delete_after=5.0)
    else:
      await interaction.response.send_message("Você não tem permissão o suficiente para realizar este comando.", ephemeral=True)

bot.run(DISCORD_BOT_TOKEN)
