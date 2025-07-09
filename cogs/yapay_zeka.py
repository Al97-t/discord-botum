# cogs/yapay_zeka.py

import discord
from discord.ext import commands
from discord import app_commands
import os
import google.generativeai as genai

# .env dosyasından aldığımız API anahtarı ile Google AI'ı yapılandırıyoruz.
# Bu kodun en üstte, sınıf tanımından önce olması önemlidir.
try:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=GEMINI_API_KEY)
except TypeError:
    print("Gemini API Anahtarı bulunamadı veya yanlış. Lütfen .env dosyanızı kontrol edin.")
    GEMINI_API_KEY = None

# Yapay zeka komutlarını içerecek olan Cog'u tanımlıyoruz.
class YapayZeka(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Kullanacağımız yapay zeka modelini burada tanımlıyoruz.
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest')

    # /sor komutunu oluşturuyoruz
    @app_commands.command(name="sor", description="PantherAI'a bir soru sorun veya onunla sohbet edin.")
    @app_commands.describe(soru="Yapay zekaya sormak istediğiniz soru veya metin")
    async def sor(self, interaction: discord.Interaction, soru: str):
        # Eğer API anahtarı yüklenmemişse komutu çalıştırma.
        if not GEMINI_API_KEY:
            return await interaction.response.send_message("Yapay zeka servisi şu anda aktif değil. Lütfen API anahtarını kontrol edin.", ephemeral=True)

        # Yapay zekanın cevabı birkaç saniye sürebilir. 
        # Bu sırada Discord'un "Bu etkileşim başarısız oldu" hatası vermemesi için
        # .defer() kullanarak "Bot düşünüyor..." mesajı gösteriyoruz.
        await interaction.response.defer(thinking=True)

        try:
            # Yapay zekadan asenkron olarak bir cevap üretmesini istiyoruz.
            response = await self.model.generate_content_async(soru)

            # Cevabı şık bir embed içinde gönderiyoruz.
            embed = discord.Embed(
                title="Yapay Zeka Diyor ki...",
                description=response.text,
                color=discord.Color.purple()
            )
            embed.set_author(name=f"Soru: {soru[:250]}", icon_url=interaction.user.display_avatar.url)
            embed.set_footer(text=f"Model: Gemini 1.5 Flash | İstek sahibi: {interaction.user.name}")
            
            # .defer() kullandığımız için cevabı .followup.send() ile gönderiyoruz.
            await interaction.followup.send(embed=embed)

        except Exception as e:
            # Eğer yapay zeka bir hata verirse (örn: uygunsuz içerik)
            await interaction.followup.send(f"Yapay zekadan cevap alınırken bir hata oluştu: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(YapayZeka(bot))