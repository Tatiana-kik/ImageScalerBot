"""
HW8 BI_Python - Telegram Bot for upscaling images.
Project team members:
     - Kikalova Tatiana
     - Жожиков Леонид
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
from cv2 import dnn_superres
from config import TOKEN


# enable logging
logging.basicConfig(
    filename='bot_logger.log',
    filemode='a',  # appendn?
    format=u'%(filename)s [ LINE:%(lineno)+3s ]'
           u'#%(levelname)+8s [%(asctime)s]  %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG
)


# global objects
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
logger = logging.getLogger()


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    """
    Start command handler.
    """
    await message.reply('Hi!\nI am Scaler Bot. Type /help '
                        'to know how to use me.')
    logger.info('start typed')


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    """
    Help comment handler.
    """
    msg = text('Send me an image as a document to scale it '
               'and write in comment '
               'the scaler (2, 3 or 4). '
               'And I will send you scaled image.')
    await message.reply(msg, parse_mode=ParseMode.MARKDOWN)
    logger.info('help typed')


async def scale_image(img_path_orig: str, img_path_scaled: str, scaler: int):
    '''
    This function resizes image by EDSR neural network.
    '''
    logger.info(f'scaling started:  orig={img_path_orig}, '
                f'scaled={img_path_scaled}, scaler={scaler}')
    # Create an SR object
    sr = dnn_superres.DnnSuperResImpl_create()

    # Read image
    image = cv2.imread(img_path_orig)

    # Detect path to model
    if scaler == 2:
        path_to_model = './EDSR_x2.pb'
    elif scaler == 3:
        path_to_model = './EDSR_x3.pb'
    else:
        path_to_model = './EDSR_x4.pb'

    # Read the desired model
    sr.readModel(path_to_model)

    # Set the desired model and scale to get correct pre- and post-processing
    sr.setModel("edsr", scaler)
    resized = sr.upsample(image)

    # Save
    cv2.imwrite(img_path_scaled, resized)
    logger.info('scaling completed')


@dp.message_handler(content_types=['document'])
async def process_document_message(msg: types.Message):
    logger.info('user input processing started')
    # check scaler
    try:
        scaler = int(msg.caption)
        logger.debug(f'users scale number={scaler} is fine')
    except BaseException as exc:
        scaler = -1
        logger.debug(f'BaseException pops out on input stage: {exc}')

    if scaler not in [2, 3, 4]:
        msg_text = text('Bad scaler. ',
                        emojize(':neutral_face:'),
                        'Use 2, 3 or 4 please.')
        await msg.reply(msg_text, parse_mode=ParseMode.MARKDOWN)
        logger.debug('user misunderstood the scaling number')
        return

    # check that document is image
    if msg.document.mime_type[0:6] != 'image/':
        msg_text = text('Bad document. ',
                        emojize(':neutral_face:'),
                        'This is not an image.')
        await msg.reply(msg_text, parse_mode=ParseMode.MARKDOWN)
        logger.debug('unknown document added instead of image')
        return

    # make paths
    user_dir = 'files/id' + str(msg.from_user.id) + '/'
    img_path_orig = user_dir + msg.document.file_name
    img_path_scaled = '{0}_{2}.{1}'.format(*img_path_orig.rsplit('.', 1) +
                                           [f'scaled_{scaler}'])
    logger.debug('paths created on input processing stage')

    # download image
    await msg.document.download(destination_file=img_path_orig)
    logger.debug('image downloaded on input processing stage')

    # scale image
    try:
        await scale_image(img_path_orig, img_path_scaled, scaler)
        logger.debug('scaling passed on input processing stage')
    except BaseException as exc:
        msg_text = text('I can\'t scale this image. Something went wrong. ',
                        emojize(':face_with_spiral_eyes:'))
        await msg.reply(msg_text, parse_mode=ParseMode.MARKDOWN)
        logger.debug('BaseException pops out of scaling on input '
                     f'processing stage:  {exc}')
        return

    # send reply
    caption = text(emojize('Scaled! :nerd_face:'))
    try:
        result_file = open(img_path_scaled, 'rb')
        await bot.send_document(msg.from_user.id, result_file,
                                caption=caption,
                                reply_to_message_id=msg.message_id)
        logger.debug('sending results to user')

    except BaseException as exc:
        msg_text = text('Scaled, but I can\'t send you the file. '
                        'Something went wrong. ',
                        emojize(':face_with_spiral_eyes:'))
        await msg.reply(msg_text, parse_mode=ParseMode.MARKDOWN)
        logger.debug('BaseException pops out in results '
                     f'sending stage:  {exc}')

    # remove user files
    shutil.rmtree(user_dir)
    logger.info('END')


@dp.message_handler(content_types=['photo'])
async def process_photo_message(msg: types.Message):
    """
    Photo handler.
    """
    message_text = text('Hm...  you sent me a photo ',
                        emojize(':astonished:.'),
                        'Sent me an image as a ',
                        bold('document'), ' (as file) please.',
                        '\nUse /help please.')
    await msg.reply(message_text, parse_mode=ParseMode.MARKDOWN)
    logger.info('user sent the photo instead of a document')


@dp.message_handler(content_types=ContentType.ANY)
async def unknown_message(msg: types.Message):
    """
    Any message handler.
    """
    message_text = text('I don\'t know what to do with this ',
                        emojize(':astonished:'),
                        '\nUse /help please.')
    await msg.reply(message_text, parse_mode=ParseMode.MARKDOWN)
    logger.info('unknown thing sent instead of a document')


if __name__ == '__main__':

    # start bot
    executor.start_polling(dp)
