# .env dosyasındaki değişkenleri yüklemek için en üstte olmalı
from dotenv import load_dotenv
load_dotenv()

# Gerekli kütüphaneler
import discord
from discord.ext import commands
import os
import database_helper 

# Botun yetkilerini (intents) belirliyoruz.
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Bot nesnesini oluşturuyoruz.
bot = commands.Bot(command_prefix="/", intents=intents)

# Bot hazır olduğunda çalışacak olan olay
@bot.event
async def on_ready():
    # Bot başlar başlamaz veritabanını ve tabloları kontrol et/oluştur.
    database_helper.init_db()
    
    print(f'{bot.user} olarak giriş yaptık ve hazırız!')
    print("-----------------------------------------")
    
    # Cogs klasöründeki tüm modülleri yüklüyoruz
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and filename != '__init__.py':
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'{filename} başarıyla yüklendi.')
            except Exception as e:
                print(f'{filename} yüklenirken bir hata oluştu: {e}')
    
    # GLOBAL SENKRONİZASYON (Herkese Açık Mod)
    try:
        print("Komutlar global olarak senkronize ediliyor...")
        synced = await bot.tree.sync()
        print(f'{len(synced)} adet slash komutu global olarak senkronize edildi.')

    except Exception as e:
        print(f'Komutlar senkronize edilirken bir hata oluştu: {e}')
    
    print("-----------------------------------------")


# Botu çalıştıracak olan TOKEN
bot.run(os.getenv("DISCORD_TOKEN"))