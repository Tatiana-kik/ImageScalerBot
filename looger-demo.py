import logging

logging.basicConfig(
    filename='dummy.log',
    filemode='w',  # appendn?
    format='%(asctime)s, %(pathname)s, %(levelname)-8s [line num:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG
)
# - %(pathname)s - %(level)s
logger = logging.getLogger()

###

logger.info('Start')

name = input('Enter name: ')
age = input('Enter age: ')

logger.debug(f'name: {name}')
logger.debug(f'age: {age}')

age_sec = int(age) * 365 * 24 * 60 * 60

print(f'{name}, your age in seconds is {age_sec}')
logger.info(f'{name}, your age in seconds is {age_sec}')

logger.info('END')
