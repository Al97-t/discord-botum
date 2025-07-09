# cogs/eglence.py

import discord
from discord.ext import commands
from discord import app_commands
import random
import aiohttp # Şaka komutu için gerekli
import os # API anahtarlarını okumak için
import google.generativeai as genai # Yapay zeka çevirisi için

# Butonları içerecek olan View sınıfımız.
# discord.ui.View'dan miras alır.
class RPSView(discord.ui.View):
    def __init__(self, *, timeout=60):
        super().__init__(timeout=timeout)
        self.user_choice = None
        self.bot_choice = None

    # Taş butonu
    @discord.ui.button(label="Taş", style=discord.ButtonStyle.secondary, emoji="🪨")
    async def rock_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.user_choice = "Taş"
        await self.process_game(interaction)

    # Kağıt butonu
    @discord.ui.button(label="Kağıt", style=discord.ButtonStyle.secondary, emoji="📄")
    async def paper_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.user_choice = "Kağıt"
        await self.process_game(interaction)

    # Makas butonu
    @discord.ui.button(label="Makas", style=discord.ButtonStyle.secondary, emoji="✂️")
    async def scissors_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.user_choice = "Makas"
        await self.process_game(interaction)
        
    async def process_game(self, interaction: discord.Interaction):
        self.bot_choice = random.choice(["Taş", "Kağıt", "Makas"])
        for item in self.children:
            item.disabled = True
        result = self.get_winner()
        embed = discord.Embed(title="Taş-Kağıt-Makas Sonucu!", color=result["color"])
        embed.add_field(name="Senin Seçimin", value=self.user_choice, inline=True)
        embed.add_field(name="Botun Seçimi", value=self.bot_choice, inline=True)
        embed.add_field(name="Sonuç", value=result["text"], inline=False)
        await interaction.response.edit_message(content=None, embed=embed, view=self)

    def get_winner(self):
        if self.user_choice == self.bot_choice:
            return {"text": "Berabere! 🤝", "color": discord.Color.greyple()}
        elif (self.user_choice == "Taş" and self.bot_choice == "Makas") or \
             (self.user_choice == "Kağıt" and self.bot_choice == "Taş") or \
             (self.user_choice == "Makas" and self.bot_choice == "Kağıt"):
            return {"text": "Tebrikler, kazandın! 🎉", "color": discord.Color.green()}
        else:
            return {"text": "Kaybettin, bot kazandı! 🤖", "color": discord.Color.red()}

# Eğlence komutlarını içerecek olan ana Cog sınıfı
class Eglence(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Gemini modelini burada bir kere başlatabiliriz
        try:
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest')
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        except Exception as e:
            print(f"Eglence Cog: Gemini modeli başlatılamadı - {e}")
            self.gemini_model = None

    @app_commands.command(name="tas_kagit_makas", description="Bot ile Taş-Kağıt-Makas oynayın.")
    async def rps_command(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Taş-Kağıt-Makas", description="Aşağıdaki butonlardan seçimini yap!", color=discord.Color.blurple())
        await interaction.response.send_message(embed=embed, view=RPSView())

    # ---------------- YENİ VE GELİŞMİŞ ŞAKA KOMUTU ----------------
    
    @app_commands.command(name="sakayap", description="Bot rastgele bir şaka yapar ve Türkçeye çevirir.")
    async def sakayap(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        
        # 1. Adım: İngilizce şakayı çek
        joke_url = "https://official-joke-api.appspot.com/random_joke"
        async with aiohttp.ClientSession() as session:
            async with session.get(joke_url) as response:
                if response.status != 200:
                    return await interaction.followup.send("Şu anda şaka makinesi bozuk, daha sonra tekrar dene!", ephemeral=True)
                joke_data = await response.json()
                english_setup = joke_data["setup"]
                english_punchline = joke_data["punchline"]

        # 2. Adım: Şakayı Türkçeye çevirt
        if not self.gemini_model:
            return await interaction.followup.send("Yapay zeka çeviri servisi şu anda aktif değil.", ephemeral=True)

        try:
            prompt = f"""Aşağıdaki İngilizce şakayı esprili bir dille Türkçeye çevir. Sadece çeviriyi yap, ekstra yorum ekleme.
            
            Kurulum: {english_setup}
            Cevap: {english_punchline}
            
            Çeviriyi şu formatta ver:
            KURULUM: [çevrilmiş kurulum]
            CEVAP: [çevrilmiş cevap]"""

            translation_response = await self.gemini_model.generate_content_async(prompt)
            parts = translation_response.text.strip().split('\n')
            turkish_setup = parts[0].replace("KURULUM:", "").strip()
            turkish_punchline = parts[1].replace("CEVAP:", "").strip()

        except Exception as e:
            return await interaction.followup.send(f"Şaka çevrilirken bir hata oluştu: {e}", ephemeral=True)

        # 3. Adım: Türkçe sonucu göster
        embed = discord.Embed(title="Bir Fıkra Zamanı! 🎤", color=discord.Color.gold())
        embed.add_field(name="Fıkra", value=f"*{turkish_setup}*", inline=False)
        embed.add_field(name="Cevap", value=f"**{turkish_punchline}**", inline=False)
        embed.set_footer(text="Official Joke API'den alındı ve Gemini ile çevrildi.")

        await interaction.followup.send(embed=embed)


# Bu cog'un ana bot dosyası tarafından yüklenebilmesi için setup fonksiyonu.
async def setup(bot: commands.Bot):
    await bot.add_cog(Eglence(bot))