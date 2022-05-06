# ImageScalerBot
Homework 8 for the BI_Python

## 1. Overview

HW8 BI_Python - Telegram Bot for upscaling images.
Project team members:
- Kikalova Tatiana
- Жожиков Леонид
- Куприянов Семён


## 2. Requirements

Code was tested on Ubuntu 20.04, Python 3.8.10.
Necessary modules are listed in requirements.txt file.
To install them - need to run `pip install -r requirements.txt`.

## 3. Usage

To use the bot follow listed steps:
1. Create your bot with `FatherBot` and get a bot TOKEN
1. Clone this repo
1. Past your TOKEN into the `config.py` file
1. Run your bot by executing `python bot.py`

## 4. Telegram Bot Implementation

For this telegram bot the `aiogram` framework was used.

## 5. Logging Implementation

"Logging" module was used for logging.
It saves all info and debug level notes in "bot_logger.log" file in "append" mode.

## 6. Image Upscaling Implementation

We used the model *EDSR*

Trained models are presented in our repository; also models can be downloaded from https://docs.opencv.org/4.x/d5/d29/tutorial_dnn_superres_upscale_image_single.html.

Model characteristics:

- Size of the model: ~38.5MB. This is a quantized version, so that it can be uploaded to GitHub. (Original was 150MB.)
- This model was trained for 3 days with a batch size of 16
- Link to implementation code: https://github.com/Saafke/EDSR_Tensorflow
- x2, x3, x4 trained models available
- Advantage: Highly accurate
- Disadvantage: Slow and large filesize
- Speed: < 3 sec for every scaling factor on 256x256 images on an Intel i7-9700K CPU.

Original paper: https://arxiv.org/pdf/1707.02921.pdf
