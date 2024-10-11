TOKEN = "TOKEN"

import discord
from discord.ext import commands
import asyncio
from aiohttp import web
import json
import logging

# Configurazione del logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
WEB_SERVER_PORT = 8080

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

CHANNEL_NAME = "verifica-ruolo"

frontend_confirmations = {}

async def handle_frontend_confirmation(request):
    data = await request.json()
    user_identifier = data.get('user_id')  # Può essere username o ID
    if user_identifier:
        frontend_confirmations[user_identifier] = True
        logger.info(f"Conferma ricevuta per utente {user_identifier}")
        return web.Response(text=json.dumps({"status": "success"}), content_type='application/json')
    logger.warning("Richiesta ricevuta senza user_id")
    return web.Response(text=json.dumps({"status": "error", "message": "User identifier not provided"}), content_type='application/json')

class InviteButton(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.Button(label="Vai su Besteam", url="https://www.besteam.io", style=discord.ButtonStyle.link))

    @discord.ui.button(label="Ho visitato Besteam", style=discord.ButtonStyle.green)
    async def confirm_visit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if any(role.name in ["President", "Player"] for role in interaction.user.roles):
            await interaction.response.send_message("Hai già un ruolo assegnato.", ephemeral=True)
            return

        user_id = str(interaction.user.id)
        user_name = interaction.user.name
        logger.info(f"Verifica conferma per utente {user_id} ({user_name})")
        
        if user_id in frontend_confirmations or user_name in frontend_confirmations:
            logger.info(f"Conferma trovata per utente {user_id} ({user_name})")
            view = RoleSelectionView()
            await interaction.response.send_message("Grazie per aver visitato Besteam! Scegli il tuo ruolo:", view=view, ephemeral=True)
        else:
            logger.info(f"Conferma non trovata per utente {user_id} ({user_name})")
            await interaction.response.send_message("In attesa di conferma dal sito Besteam. Per favore, assicurati di aver cliccato sul bottone su Besteam.", ephemeral=True)

# Funzione per gestire le richieste dal frontend
async def handle_frontend_confirmation(request):
    data = await request.json()
    user_id = data.get('user_id')
    if user_id:
        frontend_confirmations[user_id] = True
        logger.info(f"Conferma ricevuta per utente {user_id}")
        return web.Response(text=json.dumps({"status": "success"}), content_type='application/json')
    logger.warning("Richiesta ricevuta senza user_id")
    return web.Response(text=json.dumps({"status": "error", "message": "User ID not provided"}), content_type='application/json')

# Configura il server web
app = web.Application()
app.router.add_post('/confirm', handle_frontend_confirmation)

async def start_web_server():
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', WEB_SERVER_PORT)
    await site.start()
    logger.info(f"Server web in ascolto sulla porta {WEB_SERVER_PORT}")

async def main():
    await start_web_server()
    try:
        await bot.start(TOKEN)
    except KeyboardInterrupt:
        await bot.close()
    except Exception as e:
        logger.error(f"Errore durante l'avvio del bot: {e}")
