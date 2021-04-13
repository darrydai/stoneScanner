
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import configparser
import argparse
import io
import time
import numpy as np
import picamera
import sys

from PIL import Image
from tflite_runtime.interpreter import Interpreter

config = configparser.ConfigParser()
config.read('/home/pi/stoneScanner/stone_scanner.ini')
stoneImg_path=config['stamp']['stone_BG_removed']

def load_labels(path):
  with open(path, 'r') as f:
    return {i: line.strip() for i, line in enumerate(f.readlines())}


def set_input_tensor(interpreter, image):
  tensor_index = interpreter.get_input_details()[0]['index']
  input_tensor = interpreter.tensor(tensor_index)()[0]
  input_tensor[:, :] = image


def classify_image(interpreter, image, top_k=1):
  """Returns a sorted array of classification results."""
  set_input_tensor(interpreter, image)
  interpreter.invoke()
  output_details = interpreter.get_output_details()[0]
  output = np.squeeze(interpreter.get_tensor(output_details['index']))

  # If the model is quantized (uint8 data), then dequantize the results
  if output_details['dtype'] == np.uint8:
    scale, zero_point = output_details['quantization']
    output = scale * (output - zero_point)

  ordered = np.argpartition(-output, top_k)
  return [(i, output[i]) for i in ordered[:top_k]]

def stone_Dic(label_id):
  return {
    'smooth': 1,
    'wave': 2,
    'ground': 3,
    'sun': 4,
    'rose': 6,
    'snake': 7,
    'mwaji': 8,
    'land': 9,
    'unknow': 10,
    'moon': 11,
    'snow': 12,
    'mountain': 13,
    'skinny': 14,
    'empty': 15,
    }.get(label_id,'error')


def stoneMl(stoneNum):
  image = Image.open(stoneImg_path+'stone_'+str(stoneNum).zfill(4)+'.png').convert('RGB').resize((224,224),Image.ANTIALIAS)
  labels = load_labels('/home/pi/stoneScanner/ml/labels.txt')
  interpreter = Interpreter('/home/pi/stoneScanner/ml/model.tflite')
  interpreter.allocate_tensors()
  results = classify_image(interpreter, image)
  label_id, prob = results[0]
  if label_id <10 :
    label_Num = (str(labels[label_id][2:]))
  else :
    label_Num = (str(labels[label_id][3:]))
  label_Num = stone_Dic(label_Num)
  return label_Num


# def main():
#   parser = argparse.ArgumentParser(
#       formatter_class=argparse.ArgumentDefaultsHelpFormatter)
#   parser.add_argument(
#       '--model', help='File path of .tflite file.', required=True)
#   parser.add_argument(
#       '--labels', help='File path of labels file.', required=True)
#   args = parser.parse_args()

#   labels = load_labels(args.labels)

#   interpreter = Interpreter(args.model)
#   interpreter.allocate_tensors()
#   _, height, width, _ = interpreter.get_input_details()[0]['shape']

#   with picamera.PiCamera(resolution=(640, 480), framerate=30) as camera:
#     camera.shutter_speed=6000000
#     camera.start_preview()
#     try:
#       stream = io.BytesIO()
#       for _ in camera.capture_continuous(
#           stream, format='jpeg', use_video_port=True):
#         stream.seek(0)
#         image = Image.open(stream).convert('RGB').resize((width, height),
#                                                          Image.ANTIALIAS)
#         start_time = time.time()
#         results = classify_image(interpreter, image)
#         elapsed_ms = (time.time() - start_time) * 1000
#         label_id, prob = results[0]
#         stream.seek(0)
#         stream.truncate()
#         camera.annotate_text = '%s %.2f\n%.1fms' % (labels[label_id], prob,
#                                                     elapsed_ms)
#         print(labels[label_id])
#     finally:
#       camera.stop_preview()

def main():
  stoneID=stoneMl(5)
  print(stoneID)
if __name__ == '__main__':
  main()