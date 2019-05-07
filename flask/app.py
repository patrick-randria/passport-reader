#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Passport Reader
    ~~~~~~~~~~~~~~~

    A simple backend API to extract informations from a passport image file.

    :copyright: (c) 2019 by Patrick RANDRIA.
    :license: MIT, see LICENSE_FILE for more details.
"""

import os
import json
import logging
from flask import Flask, request, make_response, jsonify
from werkzeug.utils import secure_filename
from passporteye.mrz.image import MRZPipeline
from passporteye import read_mrz
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
import cv2
import numpy as np
import re

UPLOAD_FOLDER = '/uploads'
EDIT_FOLDER = '/edit'

app = Flask(__name__)

log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_fmt)

@app.route('/')
def hello_world():
    return 'Welcome ! The endpoint is at <b>/process</b>'

@app.route('/process', methods=['POST'])
def process():

    imagefile = request.files.get('imagefile', None)
    if not imagefile:
        return make_response("Missing file parameter", 400)

    filename = secure_filename(imagefile.filename)
    full_path = os.path.join(UPLOAD_FOLDER, filename)
    imagefile.save(full_path)

    # Extract informations with PassportEye
    p = MRZPipeline(full_path, extra_cmdline_params='--oem 0')
    mrz = p.result

    if mrz is None:
        return make_response("Can not read image", 400)

    mrz_data = mrz.to_dict()

    # Convert image to text
    full_content = image_to_string(full_path)
    # logging.info('full image content = %s' %(full_content))

    all_infos = {}
    all_infos['last_name'] = mrz_data['surname'].upper()
    all_infos['first_name'] = mrz_data['names'].upper()
    all_infos['country_code'] = mrz_data['country']
    all_infos['country'] = get_country_name(all_infos['country_code'])
    all_infos['nationality'] = get_country_name(mrz_data['nationality'])
    all_infos['number'] = mrz_data['number']
    all_infos['sex'] = mrz_data['sex']
    # all_infos['full_text'] = full_content
    valid_score = mrz_data['valid_score']

    # Trying to extract full name
    if all_infos['last_name'] in full_content:
        splitted_fulltext = full_content.split("\n")
        for w in splitted_fulltext:
            if all_infos['last_name'] in w:
                all_infos['last_name'] = w
                continue

    splitted_firstname = all_infos['first_name'].split(" ")
    if splitted_firstname[0] in full_content:
        splitted_fulltext = full_content.split("\n")
        for w in splitted_fulltext:
            if splitted_firstname[0] in w:
                all_infos['first_name'] = clean_name(w)
                continue

    os.remove(full_path)
    return jsonify(all_infos)

def get_country_name(country_code):
    with open('countries.json') as json_file:
        data = json.load(json_file)
        for d in data:
            if d['alpha-3'] == country_code:
                return d['name']
    return country_code

def clean_name(name):
    pattern = re.compile('([^\s\w]|_)+')
    name = pattern.sub('', name)
    return name.strip()

def image_to_string(img_path):
    """Convert image to text using tesseract OCR"""

    img = cv2.imread(img_path)

    # Extract the file name without the file extension
    file_name = os.path.basename(img_path).split('.')[0]
    file_name = file_name.split()[0]

    # Create a directory for outputs
    output_path = os.path.join(EDIT_FOLDER, file_name)
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
    # Convert to gray
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply dilation and erosion to remove some noise
    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)
    img = cv2.erode(img, kernel, iterations=1)
    # Apply blur to smooth out the edges
    img = cv2.GaussianBlur(img, (5, 5), 0)
    # Apply threshold to get image with only b&w (binarization)
    img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    # Save the filtered image in the output directory
    save_path = os.path.join(output_path, file_name + "_filter.jpg")
    cv2.imwrite(save_path, img)

    # Recognize text with tesseract for python
    result = pytesseract.image_to_string(img, lang="eng")

    os.remove(save_path)
    return result.upper()

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
