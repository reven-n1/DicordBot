import asyncio
import datetime
import os
import random
from asyncio import tasks
from discord.ext import tasks
from Bot import Bot
import youtube_dl
import discord.guild
import discord
import re

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

#  Music default queue ---------------------------------------------------------------------------->
serevers_queue_list = {655431351209689149: ['https://www.youtube.com/watch?v=421y0BbnVdQ&ab_channel=erfsfsdf!',
                                            'https://www.youtube.com/watch?v=M4iKxvfWdnM&ab_channel=K4KTUS'],
                       659869299816529920: ['https://www.youtube.com/watch?v=421y0BbnVdQ&ab_channel=erfsfsdf!',
                                            'https://www.youtube.com/watch?v=M4iKxvfWdnM&ab_channel=K4KTUS']}

is_pause = False


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, guild_id, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)

        for file in os.listdir(r"F:\Studying\DiscordBotAmia"):
            if data['id'] in file:
                old_name = os.path.basename(file)
                os.rename(old_name, old_name.replace(str(data['id']), str(guild_id)))

        filename = filename.replace(data['id'], str(guild_id))
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


#  Bot game statuses------------------------------------------------------------------------------->
status = ['Warface', 'Жизнь', 'твоего батю', 'человека', 'Detroit: Become Human', 'RAID: Shadow Legends']


intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)


def main():
    amia = Bot()

    @client.event
    async def on_ready():
        print(f'{client.user.name} - Logged')
        set_status.start()

    @client.event
    async def on_member_join(member):
        await member.send(f'Hi {member.name}')
        channel = get_channel()
        await channel.send(f'Hi {member}')

    @client.event
    async def on_message(message):
        global is_pause
        if str(message.channel) in amia.bot_channels:  # Bot works only in correct channels

            if message.author == client.user:
                return

            # Пердит в рандомного члена канала(можно и обосраться) --------------------------->
            elif message.content.startswith('!ger') or message.content.startswith('!пук'):  # Пук епт
                await message.delete()
                random_user = random.choice(client.get_guild(message.guild.id).members)
                while random_user == message.author:
                    random_user = random.choice(client.get_guild(message.guild.id).members)
                ger = amia.ger_function(message, datetime.datetime.now(), random_user)
                if 'Идет' in ger:
                    await message.channel.send(ger, delete_after=5)
                else:
                    await message.channel.send(ger)
            #  ------------------------------------------------------------------------------->

            # Gives 1 random character ------------------------------------------------------->
            elif message.content.startswith('!ark') or message.content.startswith('!арк'):
                await message.delete()
                tmp = amia.get_ark(datetime.datetime.now(), message.author.id)
                if 'Копим' in tmp:
                    await message.channel.send(tmp)
                else:
                    await ark_embed(tmp, message)
            #  ------------------------------------------------------------------------------->

            # Show bot info and commands with description ------------------------------------>
            elif message.content.startswith('!info'):
                await message.delete()
                embed = discord.Embed(color=0xff9900, title=amia.name,
                                      url=f"https://www.youtube.com/watch?v=X5ULmETDiXI")
                embed.add_field(name='Description', value=amia.bot_info['info'], inline=False)
                embed.add_field(name='Commands',
                                value=str('\n'.join(amia.get_info())),
                                inline=True)
                embed.set_thumbnail(
                    url="https://aceship.github.io/AN-EN-Tags/img/characters/char_222_bpipe_race%231.png")
                embed.set_image(url="https://aceship.github.io/AN-EN-Tags/img/characters/char_002_amiya_epoque%234.png")
                embed.set_footer(text=f'Requested by {message.author.name}')
                await message.channel.send(embed=embed, delete_after=30)
            #  ------------------------------------------------------------------------------->

            # Show ark collection ------------------------------------------------------------>
            elif message.content.startswith('!myark') or message.content.startswith('!майарк'):
                embed = discord.Embed(color=0xff9900)
                collection = amia.get_ark_collection(message.author.id)
                if not collection:
                    embed.add_field(name=f'{message.author.name} collection', value='Empty collection(((')
                else:
                    embed.add_field(name=f'{message.author.name} collection', value='\n'.join(collection))
                embed.set_thumbnail(url=message.author.avatar_url)
                embed.set_footer(text=f'Requested by {message.author.name}')
                await message.channel.send(embed=embed)
                await message.delete()
            #  ------------------------------------------------------------------------------->

            #  Changes 5 identical characters to 1 higher grade ------------------------------>
            elif message.content.startswith('!barter') or message.content.startswith('!обмен'):
                await message.delete()
                barter_list = amia.get_barter_list(message.author.id)
                if barter_list:
                    barter = amia.ark_barter(barter_list, message.author.id)
                    tmp = next(barter)
                    try:
                        while tmp:
                            await ark_embed(tmp, message)
                            tmp = next(barter)
                    except StopIteration:
                        pass
                else:
                    await message.channel.send('Нет операторов на обмен')
            #  ------------------------------------------------------------------------------->

            #  Add track to server queue ----------------------------------------------------->
            elif message.content.startswith('!add'):
                try:
                    serevers_queue_list[message.guild.id].append(message.content.split()[1])
                except:
                    serevers_queue_list[message.guild.id] = [message.content.split()[1]]
                await message.delete()
                await message.channel.send(f'Added to queue - `{message.content.split()[1]}!`')
            #  ------------------------------------------------------------------------------->

            #  Start's player ---------------------------------------------------------------->
            elif message.content.startswith('!play') or message.content.startswith('!врубай'):
                try:
                    voice_channel = message.author.voice.channel
                    q = None
                    try:
                        q = serevers_queue_list[message.guild.id]
                    except:
                        q[message.guild.id] = []
                    await voice_channel.connect()
                    await play(message, q, message.guild.id)
                except:
                    await message.channel.send("***You aren't in the voice channel***")
            #  ------------------------------------------------------------------------------->

            #  Music pause ------------------------------------------------------------------->
            elif message.content.startswith('!pause') or message.content.startswith('!пауза'):
                server = message.guild
                voice_channel = server.voice_client
                voice_channel.pause()
                is_pause = True
            #  ------------------------------------------------------------------------------->

            #  Stop's player ----------------------------------------------------------------->
            elif message.content.startswith('!stop') or message.content.startswith('!тормози'):
                server = message.guild
                voice_channel = server.voice_client
                voice_channel.stop()
            #  ------------------------------------------------------------------------------->

            #  Music resume ------------------------------------------------------------------>
            elif message.content.startswith('!resume') or message.content.startswith('!продолжай'):
                server = message.guild
                voice_channel = server.voice_client
                voice_channel.resume()
                is_pause = False
            #  ------------------------------------------------------------------------------->

            #  Start's next track ------------------------------------------------------------>
            elif message.content.startswith('!next') or message.content.startswith('!следующий'):
                server = message.guild
                voice_channel = server.voice_client
                q = None
                try:
                    q = serevers_queue_list[message.guild.id]
                except:
                    q[message.guild.id] = []
                voice_channel.stop()
                await play(message, q, message.guild.id)
            #  ------------------------------------------------------------------------------->

            # bot stop playing music and leaves form channel --------------------------------->
            elif message.content.startswith('!leave') or message.content.startswith('!вырубай'):
                await message.delete()
                voice_client = client.get_guild(message.guild.id).voice_client
                voice_client.stop()
                await voice_client.disconnect()
                await asyncio.sleep(3)
                await clear_from_music(message.guild.id)
            #  ------------------------------------------------------------------------------->

            # Clear chat messages ------------------------------------------------------------>
            elif message.content.startswith('!clear'):  # Clear command -> clear previous messages
                tmp = message.content.split()
                if len(tmp) == 2 and tmp[1].isdigit():
                    await message.channel.purge(limit=int(message.content.split()[1]))
                else:
                    await message.channel.purge(limit=amia.delete_quantity)
            #  ------------------------------------------------------------------------------->

            # If unknown command -> show message then delete it ------------------------------>
            elif message.content.startswith('!') and message.content not in amia.bot_commands:
                await message.delete()
                await message.channel.send(f'{message.content} - unknown command', delete_after=10)
                await message.channel.send('Use "!info" to see a list of commands', delete_after=10)
            #  ------------------------------------------------------------------------------->

    @tasks.loop(seconds=5)  # Set bot activity
    async def set_status():
        await client.change_presence(activity=discord.Game(random.choice(status)))

    client.run(amia.token)  # Run bot


async def get_channel():  # Return channel(переделать!!!!!!!!!!!!!!!)
    for guild in client.guilds:
        for i in guild.channels:
            if i.name == 'основной':
                await i


#  Music player ----------------------->
async def play(message, q, guild_id):
    try:
        tmp = q[0]  # Link to YouTube video
        del q[0]
        server = message.guild
        voice_channel = server.voice_client
        player = await YTDLSource.from_url(guild_id, tmp, loop=client.loop)
        voice_channel.play(player)
        await music_embed(message, tmp, player.title)

        while True:  # Check if track is on pause or it's over
            global is_pause
            if not voice_channel.is_playing() and is_pause:
                pass
            elif not voice_channel.is_playing() and not is_pause:  # If  track is over -> delete it and start new
                await clear_from_music(guild_id)
                await play(message, q, guild_id)
                break
            await asyncio.sleep(3)
    except IndexError:
        await message.channel.send('Queue is empty')


#  Set ark info to embed ----------->
async def ark_embed(tmp, message):
    # 0 - character_id      1- name     2 - description_first_part      3 - description_sec_part
    # 4 - position      5 - tags        6 - traits      7 - profession      8 - emoji       9 - rarity
    embed = discord.Embed(color=0xff9900, title=tmp[1],
                          description=str(tmp[8]) * tmp[9],
                          url=f"https://aceship.github.io/AN-EN-Tags/akhrchars.html?opname={tmp[1]}")
    embed.add_field(name='Description', value=f'{tmp[2]}\n{tmp[3]}', inline=False)
    embed.add_field(name='Position', value=tmp[4])
    embed.add_field(name='Tags', value=str(tmp[5]), inline=True)
    line = re.sub('[<@.>/]', '', tmp[6])  # Delete all tags in line
    embed.add_field(name='Traits', value=line, inline=False)
    embed.set_thumbnail(url=tmp[7])
    embed.set_image(url=f"https://aceship.github.io/AN-EN-Tags/img/characters/{tmp[0]}_1.png")
    embed.set_footer(text=f'Requested by {message.author.name}')
    await message.channel.send(embed=embed)


#  Music player control embed ---------------------->
async def music_embed(message, tmp, player_title):
    embed = discord.Embed(color=0xff9900, title=f'**Now playing:**   {player_title}')
    embed.add_field(name="YouTube", value=tmp)
    embed.set_footer(text=f'Requested by {message.author.name}')
    emb = await message.channel.send(embed=embed)
    await emb.add_reaction('▶')
    await emb.add_reaction('⏸')
    await emb.add_reaction('⏹')
    await emb.add_reaction('⏩')


#  Delete useless tracks -------------->
async def clear_from_music(guild_id):
    for file in os.listdir(r"F:\Studying\DiscordBotAmia"):
        if str(guild_id) in file:
            file_name = file
            os.remove(file_name)


if __name__ == '__main__':
    main()
