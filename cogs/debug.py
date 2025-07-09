# cogs/debug.py (GEÇİCİ TEŞHİS MODÜLÜ)

import discord
from discord.ext import commands
from discord import app_commands

class Debug(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Bu komut, botun beynindeki kayıtlı komut listesini getirir.
    @app_commands.command(name="kayitli_komutlar", description="Botun bu sunucudaki kayıtlı komutlarını listeler.")
    # Bu komutu sadece botun sahibi (yani sen) kullanabilir.
    @app_commands.checks.is_owner()
    async def list_commands(self, interaction: discord.Interaction):
        # Komutları doğrudan botun ağacından (tree) ve bu sunucuya özel olarak alıyoruz.
        guild_id = interaction.guild.id
        commands_on_server = self.bot.tree.get_commands(guild=discord.Object(id=guild_id))
        
        if not commands_on_server:
            await interaction.response.send_message("Bu sunucuda kayıtlı hiçbir komut bulunamadı.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"'{interaction.guild.name}' Sunucusundaki Gerçek Kayıtlı Komutlar",
            description="Bu liste, Discord arayüzündeki önbelleğe alınmış veriyi değil, botun hafızasındaki gerçek listeyi gösterir.",
            color=discord.Color.orange()
        )
        
        # Komutları alt alta listeliyoruz
        command_list = ""
        for command in commands_on_server:
            command_list += f"- `/{command.name}`\n"
        
        embed.add_field(name="Komutlar", value=command_list)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # Yetkisi olmayan biri denerse hata mesajı verir.
    @list_commands.error
    async def list_commands_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.NotOwner):
            await interaction.response.send_message("Bu özel bir teşhis komutudur ve sadece bot sahibi kullanabilir.", ephemeral=True)
        else:
            await interaction.response.send_message("Bir hata oluştu.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Debug(bot))