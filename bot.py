from logging import warning
import random
import discord
from discord.ext.commands import bot
from discord_components import DiscordComponents, Button, ButtonStyle
from config import settings, api_key, base_url, games
from discord.ext import commands
import datetime
from discord.utils import get
import youtube_dl
import os, sqlite3
import sys
import string, json
import requests
from PIL import Image, ImageDraw, ImageFont
import io




#PREFIX
intents = discord.Intents.all()
client = commands.Bot(command_prefix=settings['PREFIX'], intents=intents, name = settings['NAME_BOT'])
client.remove_command('help')




"""BOT_CONNECTED"""
@client.event
async def on_ready():
	DiscordComponents(client)
	print(f"{settings['NAME_BOT']} start...")
	await client.change_presence(status = discord.Status.online, activity=discord.Game(name="в GAMES_CLUB"))
	global base, cur
	base = sqlite3.connect('Secretary.db')
	cur = base.cursor()
	if base:
		print('Database connected .... OK')




"""PLAYER_JOIN"""
@client.event
async def on_member_join(member):
	await member.send(f"Привіт! Я {settings['NAME_BOT']}, перегляд команд починається з {settings['PREFIX']}help!!")
	for ch in client.get_guild(member.guild.id).channels:
		if ch.name == 'загальний':
			await client.get_channel(ch.id).send(f'{member}, круто що ти з нами в лс інфо')




"""PLAYER_LEAVE"""
@client.event
async def on_member_remove(member):
	for ch in client.get_guild(member.guild.id).channels:
		if ch.name == 'загальний':
			await client.get_channel(ch.id).send(f'{member}, нам буде не хватати тебе')




"""HELP"""
@client.command(pass_context=True)
async def help(ctx):
	emb = discord.Embed(title='HELP', colour = discord.Color.red())
	emb.add_field( name='{}clear'.format(settings['PREFIX']), value='Очистити чат')
	emb.add_field( name='{}ban'.format(settings['PREFIX']), value='Заблокувати користувача')
	emb.add_field( name='{}unban'.format(settings['PREFIX']), value='Розблокувати користувача')
	emb.add_field( name='{}kick'.format(settings['PREFIX']), value='Вигнати користувача')
	emb.add_field( name='{}time'.format(settings['PREFIX']), value='Показати час')
	emb.add_field( name='{}weather'.format(settings['PREFIX']), value='Показати погоду')
	emb.add_field( name='{}game'.format(settings['PREFIX']), value='Гра дня')
	emb.add_field( name='{}user_card'.format(settings['PREFIX']), value='Картка користувача')
	emb.add_field( name='{}join'.format(settings['PREFIX']), value='Приєднати бота до голосового чату')
	emb.add_field( name='{}play'.format(settings['PREFIX']), value='Відтворити музику(з посиланням)')
	emb.add_field( name='{}pause'.format(settings['PREFIX']), value='Призупинити музику')
	emb.add_field( name='{}resume'.format(settings['PREFIX']), value='Повторно відтворити музику')
	emb.add_field( name='{}bott'.format(settings['PREFIX']), value='Інформація про бота!')
	emb.add_field( name='{}status'.format(settings['PREFIX']), value='Інформація про ваш статус!')
	emb.set_thumbnail(url='https://www.iconsdb.com/icons/preview/white/help-xxl.png')
	await ctx.send(embed=emb)





"""TEST_BOTTON"""
@client.command(pass_context=True)
async def bott(ctx):
	await ctx.send(
		embed = discord.Embed(title="GitHub!"),
		components =[
			Button(style = ButtonStyle.green, label='Info', emoji='💁🏻'),
			Button(style = ButtonStyle.URL, label='Go!!', url ='https://github.com/tarasshutskiy'),
		]
	)
	response = await client.wait_for('button_click')
	if response.channel == ctx.channel:
		if response.component.label == 'Info':
			await response.respond(content = 'Привіт!, якщо тебе цікавить інформація стосовно роботи бота, силка буде на GitHub! ')




"""ERROR"""
@client.event
async def on_command_error(ctx, error):
	pass




"""USER_CARD"""
@client.command(pass_context=True, aliases=['я','карта']) #$я
async def user_card(ctx):
	await ctx.channel.purge(limit=1)
	img = Image.new('RGBA', (300, 150), '#232529')
	url = str(ctx.author.avatar_url)[:-10]
	response = requests.get(url, stream=True)
	response = Image.open(io.BytesIO(response.content))
	response = response.convert('RGBA')
	response = response.resize((100,100), Image.ANTIALIAS)
	img.paste(response, (15, 15, 115, 115))
	idraw = ImageDraw.Draw(img)
	name = ctx.author.name
	tag = ctx.author. discriminator
	headline= ImageFont.truetype('arial.ttf', size = 20)
	undertext = ImageFont.truetype('arial.ttf', size = 12)
	idraw.text((145, 15), f'{name}#{tag}', font = headline)
	idraw.text((145, 50), f'ID: {ctx.author.id}', font=undertext)
	img.save('user_card.png')
	await ctx.send(file=discord.File(fp='user_card.png'))




"""JOIN"""
@client.command(pass_context=True)
async def join(ctx):
	global voice
	channel = ctx.message.author.voice.channel
	voice = get(client.voice_clients, guild=ctx.guild)
	if voice and voice.is_connected():
		await voice.move_to(channel)
	else:
		voice = await channel.connect()
		await ctx.send(f'Бот приєднався до каналу: {channel}')




"""LEAVE"""
@client.command(pass_context=True)
async def leave(ctx):
	channel = ctx.message.author.voice.channel
	voice = get(client.voice_clients, guild=ctx.guild)
	if voice and voice.is_connected():
		await voice.disconnect()
	else:
		voice = await channel.connect()
		await ctx.send(f"Бот від'єднався від каналу: {channel}")




"""PLAY"""
@client.command(pass_context=True)
async def play(ctx, url : str):
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild = ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        await ctx.send(f'Бот приєднався до каналу {channel}')
    song_there = os.path.isfile('song.mp3')
    try:
        if song_there:
            os.remove('song.mp3')
            print('[log] Старий файл видалений')
    except PermissionError:
        print('[log] Не вдалося видалити старий файл')
    await ctx.send('Будь ласка очікуйте: Відбувається завантаження! ')
    voice = get(client.voice_clients, guild = ctx.guild)
    ydl_opts = {
        'format' : 'bestaudio/best',
        'postprocessors' : [{
            'key' : 'FFmpegExtractAudio',
            'preferredcodec' : 'mp3',
            'preferredquality' : '192'
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print('[log] Завантаження музики')
        ydl.download([url])
    for file in os.listdir('./'):
        if file.endswith('.mp3'):
            name = file
            print(f'[log] Перемейменування файлу: {file}')
            os.rename(file, 'song.mp3')
    voice.play(discord.FFmpegPCMAudio('song.mp3'), after = lambda e: print(f'[log] {name}, музика закінчилась відтворюватися!'))
    voice.sourse.volume = 0.07
    song_name = name.rsplit('-', 2)
    await ctx.send(f'Зараз відтварюється музика: {song_name[0]}')
#P.S. не забувайте самі приєднати до голосового каналу, тому що бот не спрацює)



"""PAUSE"""
@client.command(pass_context=True)
async def pause(ctx):
	voice = get(client.voice_clients, guild=ctx.guild)
	if voice.is_playing():
		await voice.pause()
	else:
		await ctx.send(f"Бот призупинений!!")




"""RESUME"""
@client.command(pass_context=True)
async def resume(ctx):
	voice = get(client.voice_clients, guild=ctx.guild)
	if voice.is_paused():
		await voice.resume()
	else:
		await ctx.send(f"Бот повторно відтворюється!!!")




"""DELETE_MESSAGES"""
@client.command(pass_context=True)
async def clear(ctx, amount: int):
	await ctx.channel.purge(limit=amount)
	await ctx.send(embed =discord.Embed(description = f'Видалено {amount} повідомлень!', color = 0x2ecc71))





"""STATUS"""
@client.command(pass_context=True)
async def status(ctx):
	base.execute('CREATE TABLE IF NOT EXISTS {}(userid INT, count INT)'.format(ctx.message.guild.name))
	base.commit()
	warning = cur.execute('SELECT * FROM {} WHERE userid == ?'.format(ctx.message.guild.name),(ctx.message.author.id,)).fetchone()
	if warning == None:
		await ctx.send(f"{ctx.message.author.mention}, у вас немає попереджень)")
	else:
		await ctx.send(f"{ctx.message.author.mention}, у вас {warning[1]} попереджень!!")




"""FILTER"""
@client.event
async def on_message(message):
	if {i.lower().translate(str.maketrans('','', string.punctuation)) for i in message.content.split(' ')}.intersection(set(json.load(open('cenz.json')))) !=set():
		await message.channel.send(f'{message.author.mention}, за нецензурну лексику в подальшому вас буде обмежено в правах користувача цього серверу. Якщо ситуація повториться ви будете заблоковані**')
		await message.delete()

		name = message.guild.name

		base.execute('CREATE TABLE IF NOT EXISTS {}(userid INT, count INT)'.format(name))
		base.commit()

		warning = cur.execute('SELECT * FROM {} WHERE userid == ?'.format(name),(message.author.id,)).fetchone()

		if warning == None:
			cur.execute('INSERT INTO {} VALUES(?, ?)'.format(name),(message.author.id,1))
			base.commit()
			await message.channel.send(f"{message.author.mention}, перше попередження, за третє - БАН!!(")

		elif warning[1] == 1:
			cur.execute('UPDATE {} SET count==? WHERE userid == ?'.format(name),(2,message.author.id))
			base.commit()
			await message.channel.send(f"{message.author.mention}, друге попередження, за третє - БАН!!(")

	
		elif warning[1] == 2:
			cur.execute('UPDATE {} SET count==? WHERE userid == ?'.format(name),(2,message.author.id))
			base.commit()
			await message.channel.send(f"{message.author.mention},заблокований за нецензурну лексику! ")
			await message.author.ban(reason='Ненормативна лексика')


	await client.process_commands(message)




"""KICK"""
@client.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def kick(ctx, member: discord.Member, *, reason=None):
	await ctx.channel.purge(limit=1)
	await member.kick(reason=reason)
	await ctx.send(f'kick user {member.name}')




"""BAN"""
@client.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def ban(ctx, member: discord.Member, *, reason=None):
	emb = discord.Embed(title='Ban', colour = discord.Color.red())
	await ctx.channel.purge(limit=1)
	await member.ban(reason=reason)
	emb.set_author(name = member.name, icon_url = member.avatar_url)
	emb.add_field(name='Ban User', value='Banned User: {}'.format(member.mention))
	emb.set_footer(text='Був заблокований користувачем: {}'.format(ctx.author.mention), icon_url=ctx.author.avatar_url)
	await ctx.send(embed=emb)
	# await ctx.send(f'ban user {member.name}')




"""UNBAN"""
@client.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def unban(ctx, *, member):
	await ctx.channel.purge(limit=1)
	banned_users = await ctx.guild.bans()
	for ban_entry in banned_users:
		user = ban_entry.user
		await ctx.guild.unban(user)
		await ctx.send(f'Unbanned user {user.mention}')
		return




"""TIME"""
@client.command(pass_context=True)
async def time(ctx):
	emb = discord.Embed(title='Посилання на точний час', colour = discord.Color.green(), url='https://time.is/uk/')
	emb.set_author(name = client.user.name, icon_url = client.user.avatar_url)
	emb.set_footer(text = ctx.author.name, icon_url = ctx.author.avatar_url)
	emb.set_image(url ='https://navsi200.com/media/images/main_pro_chas.2e16d0ba.fill-1200x600.jpg')
	emb.set_thumbnail(url='https://www.iconsdb.com/icons/preview/white/time-8-xxl.png')
	now_date = datetime.datetime.now()
	emb.add_field( name='Час', value='Time: {}'.format(now_date))
	await ctx.send(embed=emb)





"""GAME"""
@client.command(pass_context=True)
async def game(ctx):
	gam = random.choice(games)
	await ctx.send(f"Сьогодні ми будемо грати в {gam}")




"""WHEATER"""
@client.command(pass_context=True)
async def weather(ctx, *, city: str):
	city_name = city
	complete_url = base_url + "appid=" + api_key + "&q=" + city_name
	response = requests.get(complete_url)
	x = response.json()
	channel = ctx.message.channel
	if x["cod"] != "404":
		async with channel.typing():
			y = x["main"]
			current_temperature = y["temp"]
			current_temperature_celsiuis = str(round(current_temperature - 273.15))
			current_pressure = y["pressure"]
			current_humidity = y["humidity"]
			z = x["weather"]
			weather_description = z[0]["description"]
			embed = discord.Embed(title=f"Погода в {city_name}",color=ctx.guild.me.top_role.color,timestamp=ctx.message.created_at,)
			embed.add_field(name="Опис", value=f"**{weather_description}**", inline=False)
			embed.add_field(name="Температура(C)", value=f"**{current_temperature_celsiuis}°C**", inline=False)
			embed.add_field(name="Вологість(%)", value=f"**{current_humidity}%**", inline=False)
			embed.add_field(name="Атмосферний тиск(гПа)", value=f"**{current_pressure} гПа**", inline=False)
			embed.set_thumbnail(url="https://www.iconsdb.com/icons/preview/white/fog-day-xxl.png")
			embed.set_footer(text = ctx.author.name, icon_url = ctx.author.avatar_url)
			await channel.send(embed=embed)
	else:
		await channel.send("Місто не знайдено.")




"""MUTE"""
@client.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def user_mute(ctx, member: discord.Member,):
	emb = discord.Embed(title='Mute', colour = discord.Color.purple())
	await ctx.channel.purge(limit=1)
	mute_role = discord.utils.get(ctx.message.guild.roles, name='mute')
	await member.add_roles(mute_role)
	emb.set_author(name = member.name, icon_url = member.avatar_url)
	emb.add_field(name='Mute User', value='Muted User: {}'.format(member.mention))
	emb.set_footer(text='Був замутчено користувачем: {}'.format(ctx.author.name), icon_url=ctx.author.avatar_url)
	emb.set_thumbnail(url='https://www.iconsdb.com/icons/preview/white/mute-2-xxl.png')
	await ctx.send(embed=emb)




"""UNMUTE"""
@client.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def un_mute(ctx, member: discord.Member,):
	emb = discord.Embed(title='Unmute', colour = discord.Color.blue())
	await ctx.channel.purge(limit=1)
	mute_role = discord.utils.get(ctx.message.guild.roles, name='mute')
	await member.remove_roles(mute_role)
	emb.set_author(name = member.name, icon_url = member.avatar_url)
	emb.add_field(name='Unmute User', value='Unmuted User: {}'.format(member.mention))
	emb.set_footer(text='Було розмутчено користувачем: {}'.format(ctx.author.name), icon_url=ctx.author.avatar_url)
	emb.set_thumbnail(url='https://www.iconsdb.com/icons/preview/white/volume-up-2-xxl.png')
	await ctx.send(embed=emb)




"""CLEAR_ERROR"""
@clear.error
async def clear_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send(f'{ctx.author.name}, забули вказати кількість повідомлень!')
	if isinstance(error, commands.MissingPermissions):
		await ctx.send(f'{ctx.author.name}, у вас недостатньо прав!')




"""WEATHER_ERROR"""
@weather.error
async def weather_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send(f'{ctx.author.name}, забули вказати місто!')
	if isinstance(error, commands.MissingPermissions):
		await ctx.send(f'{ctx.author.name}, у вас недостатньо прав!')




"""PLAY_ERROR"""
@play.error
async def play_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send(f'{ctx.author.name}, забули вказати посилання на музику!!')
	if isinstance(error, commands.MissingPermissions):
		await ctx.send(f'{ctx.author.name}, у вас недостатньо прав!')




"""USER_CARD_ERROR"""
@user_card.error
async def user_card_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send(f'{ctx.author.name}, забули вказати користувача!!')
	if isinstance(error, commands.MissingPermissions):
		await ctx.send(f'{ctx.author.name}, у вас недостатньо прав!')




"""BAN_ERROR"""
@ban.error
async def ban_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send(f'{ctx.author.name}, забули вказати користувача!!')
	if isinstance(error, commands.MissingPermissions):
		await ctx.send(f'{ctx.author.name}, у вас недостатньо прав!')




"""BAN_ERROR"""
@unban.error
async def unban_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send(f'{ctx.author.name}, забули вказати користувача!!')
	if isinstance(error, commands.MissingPermissions):
		await ctx.send(f'{ctx.author.name}, у вас недостатньо прав!')




"""MUTE_ERROR"""
@user_mute.error
async def user_mute_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send(f'{ctx.author.name}, забули вказати користувача!!')
	if isinstance(error, commands.MissingPermissions):
		await ctx.send(f'{ctx.author.name}, у вас недостатньо прав!')




"""UNMUTE_ERROR"""
@un_mute.error
async def un_mute_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send(f'{ctx.author.name}, забули вказати користувача!!')
	if isinstance(error, commands.MissingPermissions):
		await ctx.send(f'{ctx.author.name}, у вас недостатньо прав!')




"""KICK_ERROR"""
@un_mute.error
async def kick_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send(f'{ctx.author.name}, забули вказати користувача!!')
	if isinstance(error, commands.MissingPermissions):
		await ctx.send(f'{ctx.author.name}, у вас недостатньо прав!')




#Start BOT
client.run((settings['TOKEN']))