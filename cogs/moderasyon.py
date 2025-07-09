# cogs/moderasyon.py

import discord
from discord.ext import commands
from discord import app_commands
import datetime

# Bu cog'un, bir üst klasördeki database_helper.py dosyasını bulabilmesi için
# projenin ana dizinini Python'un arama yoluna ekliyoruz.
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import database_helper

# Moderasyon komutlarını içerecek olan Cog'u tanımlıyoruz.
class Moderasyon(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # /temizle komutu
    @app_commands.command(name="temizle", description="Belirtilen miktarda mesajı kanaldan siler.")
    @app_commands.describe(miktar="Silinecek mesaj sayısı (1-100 arası)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def temizle(self, interaction: discord.Interaction, miktar: int):
        silinen_mesajlar = await interaction.channel.purge(limit=miktar)
        await interaction.response.send_message(f'{len(silinen_mesajlar)} adet mesaj başarıyla silindi.', ephemeral=True)

    @temizle.error
    async def temizle_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("Bu komutu kullanmak için 'Mesajları Yönet' yetkisine sahip olmalısın!", ephemeral=True)
        else:
            await interaction.response.send_message("Komutu kullanırken bir hata oluştu.", ephemeral=True)
            print(error)

    # /kick komutu
    @app_commands.command(name="kick", description="Belirtilen kullanıcıyı sunucudan atar.")
    @app_commands.describe(kullanici="Atılacak kullanıcıyı etiketleyin", sebep="Atılma sebebi (isteğe bağlı)")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, kullanici: discord.Member, sebep: str = "Belirtilmedi"):
        if kullanici.id == self.bot.user.id or kullanici.id == interaction.user.id:
            return await interaction.response.send_message("Kendini veya beni atamazsın!", ephemeral=True)
        if interaction.user.top_role <= kullanici.top_role:
             return await interaction.response.send_message("Kendi rolünden daha yüksek veya aynı roldeki birini atamazsın!", ephemeral=True)
        try:
            await kullanici.send(f"**{interaction.guild.name}** sunucusundan atıldın.\n**Sebep:** {sebep}")
        except discord.errors.Forbidden:
            pass
        await kullanici.kick(reason=f"Yetkili: {interaction.user.name} | Sebep: {sebep}")
        embed = discord.Embed(title="✅ Kullanıcı Atıldı", description=f"**{kullanici.name}** adlı kullanıcı sunucudan başarıyla atıldı.", color=discord.Color.red())
        embed.add_field(name="Atılan Kullanıcı", value=kullanici.mention, inline=True)
        embed.add_field(name="Yetkili", value=interaction.user.mention, inline=True)
        embed.add_field(name="Sebep", value=sebep, inline=False)
        embed.set_thumbnail(url=kullanici.display_avatar.url)
        await interaction.response.send_message(embed=embed)
    
    @kick.error
    async def kick_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("Bu komutu kullanmak için 'Üyeleri At' yetkisine sahip olmalısın!", ephemeral=True)
        else:
            await interaction.response.send_message("Komutu kullanırken bir hata oluştu.", ephemeral=True)
            print(error)
            
    # ---------------- YENİ EKLENEN UYARI SİSTEMİ KOMUTLARI ----------------

    @app_commands.command(name="uyar", description="Bir kullanıcıyı uyarır ve veritabanına kaydeder.")
    @app_commands.describe(kullanici="Uyarılacak kullanıcı", sebep="Uyarı sebebi")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def uyar(self, interaction: discord.Interaction, kullanici: discord.Member, sebep: str):
        database_helper.add_warning(kullanici.id, interaction.user.id, sebep)
        embed = discord.Embed(title="⚠️ Kullanıcı Uyarıldı", description=f"{kullanici.mention} adlı kullanıcı başarıyla uyarıldı.", color=discord.Color.yellow())
        embed.add_field(name="Yetkili", value=interaction.user.mention, inline=True)
        embed.add_field(name="Sebep", value=sebep, inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="uyarilari_goster", description="Bir kullanıcının aldığı tüm uyarıları gösterir.")
    @app_commands.describe(kullanici="Uyarıları gösterilecek kullanıcı")
    async def uyarilari_goster(self, interaction: discord.Interaction, kullanici: discord.Member):
        warnings = database_helper.get_warnings(kullanici.id)
        embed = discord.Embed(title=f"{kullanici.name} Adlı Kullanıcının Uyarıları", color=discord.Color.orange())
        if not warnings:
            embed.description = "Bu kullanıcının hiç uyarısı yok. Tertemiz! ✨"
        else:
            embed.description = f"Toplam {len(warnings)} adet uyarı bulundu."
            for idx, warning in enumerate(warnings, start=1):
                moderator_id, reason, timestamp_str = warning
                timestamp_dt = datetime.datetime.fromisoformat(timestamp_str)
                discord_timestamp = f"<t:{int(timestamp_dt.timestamp())}:R>"
                embed.add_field(name=f"Uyarı #{idx} ({discord_timestamp})", value=f"**Sebep:** {reason}\n**Yetkili:** <@{moderator_id}>", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

# Bu cog'un ana bot dosyası tarafından yüklenebilmesi için setup fonksiyonu.
async def setup(bot: commands.Bot):
    await bot.add_cog(Moderasyon(bot))