import os
import psycopg2
# import config
# from config import tests as TESTS
# from config import ADMINS
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram.filters import Command, CommandStart
from aiogram.enums import ParseMode
from aiogram.utils.media_group import MediaGroupBuilder

from dotenv import load_dotenv

load_dotenv()



try:
	db = psycopg2.connect(user=os.environ.get("POSTGRES_USER"),
					      password=os.environ.get("POSTGRES_PASSWORD"),
						  host='localhost', port='5432',
						  database=os.environ.get("POSTGRES_DB"))
	cursor = db.cursor()
except Exception as e:
	raise Exception('Some problems with database, {}'.format(e))

cursor.execute('''CREATE TABLE IF NOT EXISTS projects (
	id SERIAL PRIMARY KEY,
	name TEXT,
	deadline TIMESTAMP WITH TIMEZONE,
	subtasks INTEGER,
	parent_id INTEGER REFERENCES projects(id)
)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS subtasks (
	project_id INTEGER REFERENCES projects(id)
	no INTEGER PRIMARY KEY,
	deadline TIMESTAMP WITH TIMEZONE,
	done BOOLEAN
)''')

db.commit()

print('Print')

exit()

bot = Bot(token=os.environ.get("BOT_TOKEN"))
dp = Dispatcher()
work = Work(db)

async def check_subscription(channel, user_id) -> bool:
	try:
		status = await bot.get_chat_member(chat_id=channel,
										   user_id=user_id)
	except Exception as e:
		print(f"Error occured: {e}")
		return None
	return status.status != 'left'

async def send_results(chat_id, message_to_delete_id, user_id, test_name):
	await bot.delete_message(chat_id, message_to_delete_id)
	await bot.send_photo(chat_id,
						 FSInputFile(work.generate_picture(user_id, test_name)),
						 caption="Результаты вашего теста.",
						 reply_markup=config.gen_about_keyboard(test_name))
	work.erase_answers(user_id, test_name)

async def send_next_question(message, test_name, question_num):
	questions = TESTS[test_name]['questions']
	test_len = len(questions)
	# if isinstance(questions, int):
	# 	test_len = questions
	# elif isinstance(questions, list):
	# 	test_len = len(questions)
	if 'text' in questions[question_num]:
		await bot.edit_message_text(message_id=message.message_id,
								chat_id=message.chat.id,
								text=f"{question_num + 1}/{test_len} {TESTS[test_name]['questions'][question_num]['text']}",
								parse_mode=ParseMode.HTML,
								reply_markup=work.generate_test_answers(test_name, question_num))
	elif question_num == 0:
		await bot.send_photo(message.chat.id,
							 FSInputFile(f"./questions_photos/{test_name}/{question_num}.png"),
							 reply_markup=work.generate_test_answers(test_name, question_num))
		await bot.delete_message(message.chat.id, message.message_id)
	else:
		await bot.edit_message_media(media=InputMediaPhoto(media=FSInputFile(f"./questions_photos/{test_name}/{question_num}.png")),
									 message_id=message.message_id,
									 chat_id=message.chat.id,
									 reply_markup=work.generate_test_answers(test_name, question_num))


@dp.message(F.text, Command("db"))
async def db_data(message: Message):
	if message.from_user.id not in config.ADMINS:
		return
	cursor.execute("SELECT DISTINCT user_id FROM users")
	check = cursor.fetchall()
	t = '' 
	for i in check:
		t += str(i[0]) + '\n'
	f = open('users.txt', mode = 'w', encoding ='latin-1')
	f.write(t)
	f.close()
	await message.reply_document(FSInputFile(f"./users.txt"))

@dp.message(F.text, Command("stat"))
async def db_stat(message: Message):
	if message.from_user.id not in config.ADMINS:
		return
	await bot.send_message(chat_id=message.chat.id, text=work.get_ref_statistic())

@dp.message(F.text, CommandStart())
async def start(message: Message):
	print(f"/start from {message.from_user.id}")
	ref_url = None
	if message.text != '/start':
		ref_url = message.text.split(' ')[-1]
	work.start(message.chat.id, ref_url)
	await bot.send_message(chat_id=message.chat.id,
						   text=f'В нашем боте вы можете бесплатно проходить психологические личностные тесты, многие из которых основаны на рецензируемых научных исследованиях и разработаны экспертами в области психометрии.',
						   parse_mode=ParseMode.HTML,
						   reply_markup=config.start_keyboard)


@dp.callback_query()
async def callback_query(call: CallbackQuery):
	print(f"{call.data} from {call.from_user.id}")
	if call.data.endswith('_test_selected'):
		test_name = call.data.split('_')[0]
		test_cfg = TESTS[test_name]
		questions_count = len(test_cfg['questions'])
		description = ''
		if test_cfg.get('description') is not None:
			description = f"{test_cfg['description']}\n\n"
		welcome_question = ''
		if 'welcome_question' in test_cfg and test_cfg['welcome_question'] is not None:
			welcome_question = test_cfg['welcome_question'] + ' '
		welcoming = ''
		if 'welcome_question' in test_cfg:
			welcoming = f"Для каждого следующего утверждения укажите, насколько Вы с ним согласны. В тесте {questions_count} вопрос{config.get_ending(questions_count)}."
		await bot.edit_message_text(message_id=call.message.message_id,
							  		chat_id=call.message.chat.id,
									text=f"{description}{welcome_question}{welcoming}",
									parse_mode=ParseMode.HTML,
									reply_markup=config.gen_start_test_keyboard(test_name))

	if call.data.endswith('_test_started'):
		test_name = call.data.split('_')[0]
		await send_next_question(call.message, test_name, 0)
		work.erase_answers(call.from_user.id, test_name)

	elif call.data.startswith('q_'):
		_, test_name, question, param, answer = call.data.split('_')
		question = int(question)
		answer = int(answer)
		work.write_answer(call.from_user.id, test_name, question, param, answer)
		if question < len(TESTS[test_name]['questions']) - 1:
			await send_next_question(call.message, test_name, question + 1)
			return
		required_channel = TESTS[test_name].get('required_channel')
		if required_channel is not None:
			subscribed = await check_subscription(required_channel['id'], call.from_user.id)
			if subscribed is None:
				if call.from_user.id in ADMINS:
					await bot.send_message(chat_id=call.message.chat.id,
										   text=f"Бот не может проверить подписку на {required_channel['link']}, так как не добавлен в админы этого канала. Пропускаю без проверки.\n\nЭто сообщение видят только администраторы.",
									 	   parse_mode=ParseMode.HTML)
			elif not subscribed:
				await bot.delete_message(call.message.chat.id, call.message.message_id)
				await bot.send_message(chat_id=call.message.chat.id,
									   text='Для получения результатов надо подписаться на наш канал:',
								       parse_mode=ParseMode.HTML,
									   reply_markup=config.gen_check_sub_keyboard(test_name, required_channel['link']))
				return
		await send_results(call.message.chat.id, call.message.message_id, call.from_user.id, test_name)

	elif call.data.startswith('goto_'):
		_, test_name, to_question = call.data.split('_')
		question = int(to_question)
		work.delete_answer(call.from_user.id, test_name, question)
		await send_next_question(call.message, test_name, question)

	elif call.data.startswith('about_'):
		_, test_name = call.data.split('_')
		media_group = MediaGroupBuilder(caption="Обьяснение результатов теста.")
		directory = os.fsencode(f"./abouts/{test_name}")
		for file in os.listdir(directory):
			filename = os.fsdecode(file)
			media_group.add(type="photo",
							media=FSInputFile(f"./abouts/{test_name}/{filename}"))
		await bot.send_media_group(chat_id=call.message.chat.id,
								   media=media_group.build())

	elif call.data.startswith('check_sub_'):
		_, _, test_name = call.data.split('_')
		if not await check_subscription(TESTS[test_name]['required_channel']['id'], call.from_user.id):
			await call.answer('Вы не подписались на канал!')
			return
		await send_results(call.message.chat.id, call.message.message_id, call.from_user.id, test_name)


async def main():
    await dp.start_polling(bot) # skip_updates=False)

if __name__ == "__main__":
    asyncio.run(main())