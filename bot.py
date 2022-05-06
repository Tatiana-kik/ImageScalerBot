"""
HW8 BI_Python - Telegram Bot for upscaling images.
Project team members:
     - Kikalova Tatiana
     - Жожиков Леонид
     - Муроцмев Антон
     - Куприянов Семён
"""
import logging
from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.utils.emoji import emojize
from aiogram.dispatcher import Dispatcher
from aiogram.types.message import ContentType
from aiogram.utils.markdown import text, bold
from aiogram.types import ParseMode
import shutil
import cv2
from config import TOKEN

# enable logging
logging.basicConfig(
    filename='bot_logger.log',
    filemode='a',  # appendn?
    format=u'%(filename)s [ LINE:%(lineno)+3s ]'u'#%(levelname)+8s [%(asctime)s]  %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG
)

# global objects
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
logger = logging.getLogger()


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply('Hi!\nI am Scaler Bot. Type /help '
                        'to know how to use me.')
    logger.info('start typed')


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    msg = text('Send me an image as a document to scale it '
               'and write in comment '
               'the scaler (any number >1 and <=5). '
               'And I will send you scaled image.')
    await message.reply(msg, parse_mode=ParseMode.MARKDOWN)
    logger.info('help typed')


async def scale_image(img_path_orig: str, img_path_scaled: str, scaler: float):
    """
    This function resizes image by opencv.
    Probably need to change it and use NN for upscaling.
    """
    logger.info('scaling started')
    print(f'orig={img_path_orig}, scaled={img_path_scaled}, scaler=(scaler)')
    # open image by opencv
    img = cv2.imread(img_path_orig, cv2.IMREAD_UNCHANGED)
    print('Original Dimensions : ', img.shape)
    # calculate new demension
    width = int(img.shape[1] * scaler)
    height = int(img.shape[0] * scaler)
    dim = (width, height)
    # resize image
    resized = cv2.resize(img, dim, interpolation=cv2.INTER_LINEAR)
    print('Resized Dimensions : ', resized.shape)
    cv2.imwrite(img_path_scaled, resized)
    logger.info('scaling completed')


@dp.message_handler(content_types=['document'])
async def process_document_message(msg: types.Message):
    logger.info('user input processing started')
    # check scaler
    try:
        scaler = float(msg.caption)
        logger.debug('users scale number is fine')
    except BaseException:
        scaler = -1
        logger.debug('BaseException pops out on input stage')

    if not 1 < scaler <= 5:
        msg_text = text(emojize('Bad scaler. :neutral_face:'),
                        'Use any number >1 and <=5 please.')
        await msg.reply(msg_text, parse_mode=ParseMode.MARKDOWN)
        logger.debug('user misunderstood the scaling number')
        return

    # check that document is image
    if msg.document.mime_type[0:6] != 'image/':
        msg_text = text(emojize('Bad document. :neutral_face:'),
                        'This is not an image.')
        await msg.reply(msg_text, parse_mode=ParseMode.MARKDOWN)
        logger.debug('unknown document added instead of image')
        return

    # make pahts
    user_dir = 'files/id' + str(msg.from_user.id) + '/'
    img_path_orig = user_dir + msg.document.file_name
    img_path_scaled = '{0}_{2}.{1}'.format(*img_path_orig.rsplit('.', 1) +
                                           [f'scaled_{scaler}'])
    logger.debug('paths created on input processing stage')

    # download image
    await msg.document.download(img_path_orig)
    logger.debug('image downloaded on input processing stage')

    # scale image
    try:
        await scale_image(img_path_orig, img_path_scaled, scaler)
        logger.debug('scaling passed on input processing stage')
    except BaseException:
        msg_text = text(emojize('I can\'t scale this image. '
                                'Something went wrong. '
                                ':face_with_spiral_eyes:'))
        await msg.reply(msg_text, parse_mode=ParseMode.MARKDOWN)
        logger.debug('BaseException pops out of scaling on input processing stage')
        return

    # send reply
    caption = text(emojize('Scaled! :nerd_face:'))
    try:
        result_file = open(img_path_scaled, 'rb')
        await bot.send_document(msg.from_user.id, result_file,
                                caption=caption,
                                reply_to_message_id=msg.message_id)
        logger.debug('sending results to user')

    except BaseException:
        msg_text = text('Scaled, but I can\'t send you the file. '
                        'Something went wrong. ',
                        emojize(':face_with_spiral_eyes:'))
        await msg.reply(msg_text, parse_mode=ParseMode.MARKDOWN)
        logger.debug('BaseException pops out in results sending stage')

    # remove user files
    shutil.rmtree(user_dir)
    logger.info('END')


@dp.message_handler(content_types=['photo'])
async def process_photo_message(msg: types.Message):
    message_text = text(emojize('Hm...  you sent me a photo :astonished:.'),
                        'Sent me an image as a ',
                        bold('document'), ' (as file) please.',
                        '\nUse /help please.')
    await msg.reply(message_text, parse_mode=ParseMode.MARKDOWN)
    logger.info('user sent the photo instead of a document')


@dp.message_handler(content_types=ContentType.ANY)
async def unknown_message(msg: types.Message):
    message_text = text('I don\'t know what to do with this ',
                        emojize(':astonished:'),
                        '\nUse /help please.')
    await msg.reply(message_text, parse_mode=ParseMode.MARKDOWN)
    logger.info('unknown thing sent instead of a document')


if __name__ == '__main__':

    # start bot
    executor.start_polling(dp)

