# cogs/utility.py

import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Select, View # Menü ve View için gerekli

# Yardım menüsünün kendisini ve mantığını içeren View sınıfı
class HelpSelectView(View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=120)
        self.bot = bot
        self.add_item(self.create_select_menu())

    def create_select_menu(self):
        # Menüdeki seçenekleri tanımlıyoruz
        select_options = [
            discord.SelectOption(label="Ana Sayfa", emoji="🏠", description="Yardım menüsünün ana sayfasına dön."),
            discord.SelectOption(label="Eğlence", emoji="🎮", description="Eğlence ve oyun komutlarını göster."),
            discord.SelectOption(label="Moderasyon", emoji="🛡️", description="Sunucu yönetimi ve moderasyon komutlarını göster."),
            discord.SelectOption(label="Yardımcı Araçlar", emoji="🛠️", description="Bilgi ve diğer yardımcı komutları göster."),
            discord.SelectOption(label="Yapay Zeka & API", emoji="🤖", description="Yapay zeka ve internet komutlarını göster."),
        ]
        select = Select(placeholder="Bir kategori seç...", options=select_options)
        select.callback = self.select_callback
        return select

    async def select_callback(self, interaction: discord.Interaction):
        choice = interaction.data["values"][0]
        embed = discord.Embed(title=f"{choice} Komutları", color=discord.Color.blue())

        if choice == "Eğlence":
            embed.description = "Sunucuda eğlenmek ve oynamak için kullanabileceğin komutlar:"
            embed.add_field(name="/tas_kagit_makas", value="Bot ile Taş-Kağıt-Makas oynayın.", inline=False)
            embed.add_field(name="/sakayap", value="Bot rastgele bir şaka yapar ve Türkçeye çevirir.", inline=False)
        elif choice == "Moderasyon":
            embed.description = "Sunucuyu yönetmek ve düzeni sağlamak için kullanabileceğin komutlar:"
            embed.add_field(name="/temizle", value="Belirtilen miktarda mesajı siler.", inline=False)
            embed.add_field(name="/kick", value="Bir üyeyi sunucudan atar.", inline=False)
            embed.add_field(name="/uyar", value="Bir üyeyi uyarır.", inline=False)
            embed.add_field(name="/uyarilari_goster", value="Bir üyenin uyarılarını listeler.", inline=False)
        elif choice == "Yardımcı Araçlar":
            embed.description = "Bilgi almak ve çeşitli araçları kullanmak için komutlar:"
            embed.add_field(name="/ping", value="Botun gecikme süresini gösterir.", inline=False)
            embed.add_field(name="/selam", value="Bot size selam verir.", inline=False)
            embed.add_field(name="/kullanici_bilgi", value="Kullanıcı bilgilerini gösterir.", inline=False)
            embed.add_field(name="/yardim", value="Bu yardım menüsünü açar.", inline=False)
        elif choice == "Yapay Zeka & API":
            embed.description = "Yapay zeka ve internet tabanlı komutlar:"
            embed.add_field(name="/sor", value="Yapay zekaya bir soru sorun.", inline=False)
            embed.add_field(name="/hava_durumu", value="Bir şehrin hava durumunu öğrenin.", inline=False)
        else: # Ana Sayfa seçilirse
            embed.title = "Yardım Menüsü"
            embed.description = f"Merhaba! Ben {self.bot.user.name}, senin sunucu asistanın.\n\nAşağıdaki menüden komut kategorilerini seçerek hakkımda daha fazla bilgi alabilirsin."

        await interaction.response.edit_message(embed=embed)

# Ana Utility Cog sınıfı
class Utility(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Botun gecikme süresini gösterir.")
    async def ping(self, interaction: discord.Interaction):
        gecikme = round(self.bot.latency * 1000)
        embed = discord.Embed(title="Pong! 🏓", description=f"Botun gecikme süresi: **{gecikme}ms**", color=discord.Color.green())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="selam", description="Bot size selam verir.")
    async def selam(self, interaction: discord.Interaction):
        user_mention = interaction.user.mention
        await interaction.response.send_message(f"Merhaba {user_mention}!")

    @app_commands.command(name="kullanici_bilgi", description="Belirtilen kullanıcının veya kendinizin bilgilerini gösterir.")
    @app_commands.describe(kullanici="Bilgilerini görmek istediğiniz kullanıcı")
    async def kullanici_bilgi(self, interaction: discord.Interaction, kullanici: discord.Member = None):
        target = kullanici or interaction.user
        embed = discord.Embed(title=f"{target.name} Kullanıcısının Bilgileri", description=f"İşte {target.mention} hakkında bazı detaylar.", color=discord.Color.blue())
        embed.set_thumbnail(url=target.avatar.url)
        embed.add_field(name="Kullanıcı ID", value=target.id, inline=False)
        embed.add_field(name="Discord'a Katılma Tarihi", value=f"<t:{int(target.created_at.timestamp())}:F>", inline=True)
        embed.add_field(name="Sunucuya Katılma Tarihi", value=f"<t:{int(target.joined_at.timestamp())}:F>", inline=True)
        roller = [role.mention for role in target.roles[1:]]
        roller.reverse()
        if roller:
            embed.add_field(name=f"Roller ({len(roller)})", value=" ".join(roller), inline=False)
        else:
            embed.add_field(name="Roller", value="Kullanıcının rolü yok.", inline=False)
        embed.set_footer(text=f"İstek sahibi: {interaction.user.name}", icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed)

    # --- YENİ EKLENEN YARDIM KOMUTU ---
    @app_commands.command(name="yardim", description="Botun tüm komutlarını gösteren interaktif bir menü açar.")
    async def yardim(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Yardım Menüsü",
            description=f"Merhaba! Ben {self.bot.user.name}, senin sunucu asistanın.\n\nAşağıdaki menüden komut kategorilerini seçerek hakkımda daha fazla bilgi alabilirsin.",
            color=discord.Color.dark_magenta()
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        await interaction.response.send_message(embed=embed, view=HelpSelectView(bot=self.bot))

# Cog'un bota eklenmesi için setup fonksiyonu
async def setup(bot: commands.Bot):
    await bot.add_cog(Utility(bot))