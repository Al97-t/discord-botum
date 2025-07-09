# cogs/api_komutlari.py

import discord
from discord.ext import commands
from discord import app_commands
import os
import aiohttp # Asenkron HTTP istekleri için

class ApiKomutlari(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="hava_durumu", description="Belirtilen şehrin güncel hava durumu bilgisini gösterir.")
    @app_commands.describe(sehir="Hava durumunu öğrenmek istediğiniz şehir")
    async def hava_durumu(self, interaction: discord.Interaction, sehir: str):
        # .env dosyasından API anahtarımızı çekiyoruz.
        API_KEY = os.getenv("OPENWEATHER_API_KEY")
        if not API_KEY:
            await interaction.response.send_message("Hava durumu API anahtarı bulunamadı!", ephemeral=True)
            return

        # OpenWeatherMap API'sine göndereceğimiz isteğin URL'ini oluşturuyoruz.
        # units=metric -> Sıcaklığı Santigrat (°C) olarak alır.
        # lang=tr -> Açıklamaları Türkçe alır.
        url = f"https://api.openweathermap.org/data/2.5/weather?q={sehir}&appid={API_KEY}&units=metric&lang=tr"

        # aiohttp kullanarak API'ye asenkron bir GET isteği gönderiyoruz.
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                # Eğer şehir bulunamazsa (404 hatası), kullanıcıya bildir.
                if response.status == 404:
                    await interaction.response.send_message(f"'{sehir}' adında bir şehir bulunamadı. Lütfen kontrol edip tekrar dene.", ephemeral=True)
                    return
                # Başka bir hata olursa genel bir mesaj gönder.
                elif response.status != 200:
                    await interaction.response.send_message("Hava durumu bilgisi alınırken bir hata oluştu.", ephemeral=True)
                    return
                
                # API'den gelen cevabı JSON formatında alıyoruz.
                data = await response.json()

        # JSON verisinden ihtiyacımız olan bilgileri ayıklıyoruz.
        sehir_adi = data["name"]
        ulke = data["sys"]["country"]
        sicaklik = data["main"]["temp"]
        hissedilen_sicaklik = data["main"]["feels_like"]
        aciklama = data["weather"][0]["description"].title() # baş harfi büyük olsun
        ikon_kodu = data["weather"][0]["icon"]
        ikon_url = f"https://openweathermap.org/img/wn/{ikon_kodu}@2x.png"

        # Bilgileri göstermek için şık bir Embed oluşturuyoruz.
        embed = discord.Embed(
            title=f"{sehir_adi}, {ulke} Hava Durumu",
            description=f"**{aciklama}**",
            color=discord.Color.orange()
        )
        embed.set_thumbnail(url=ikon_url)
        embed.add_field(name="Sıcaklık", value=f"{sicaklik}°C", inline=True)
        embed.add_field(name="Hissedilen", value=f"{hissedilen_sicaklik}°C", inline=True)
        embed.set_footer(text="Veriler OpenWeatherMap tarafından sağlanmaktadır.")

        # Hazırladığımız embed'i kullanıcıya gönderiyoruz.
        await interaction.response.send_message(embed=embed)


# Bu cog'un ana bot dosyası tarafından yüklenebilmesi için setup fonksiyonu.
async def setup(bot: commands.Bot):
    await bot.add_cog(ApiKomutlari(bot))