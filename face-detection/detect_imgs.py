"""
Modified code from https://github.com/Linzaer/Ultra-Light-Fast-Generic-Face-Detector-1MB
"""
import argparse
import os
import sys
import time

from cv2 import * 

from vision.ssd.config.fd_config import define_img_size

parser = argparse.ArgumentParser(
    description='detect_imgs')

parser.add_argument('--net_type', default="RFB", type=str,
                    help='The network architecture ,optional: RFB (higher precision) or slim (faster)')
parser.add_argument('--input_size', default=640, type=int,
                    help='define network input size,default optional value 128/160/320/480/640/1280')
parser.add_argument('--threshold', default=0.6, type=float,
                    help='score threshold')
parser.add_argument('--candidate_size', default=1500, type=int,
                    help='nms candidate size')
parser.add_argument('--path', default="imgs", type=str,
                    help='imgs dir')
parser.add_argument('--test_device', default="cpu", type=str,
                    help='cuda:0 or cpu')
args = parser.parse_args()
define_img_size(args.input_size)  # must put define_img_size() before 'import create_mb_tiny_fd, create_mb_tiny_fd_predictor'

from vision.ssd.mb_tiny_fd import create_mb_tiny_fd, create_mb_tiny_fd_predictor
from vision.ssd.mb_tiny_RFB_fd import create_Mb_Tiny_RFB_fd, create_Mb_Tiny_RFB_fd_predictor

result_path = "./results"
label_path = "./labels.txt"
test_device = args.test_device

class_names = [name.strip() for name in open(label_path).readlines()]

model_path = "./model.pth"
net = create_Mb_Tiny_RFB_fd(len(class_names), is_test=True, device=test_device)
predictor = create_Mb_Tiny_RFB_fd_predictor(net, candidate_size=args.candidate_size, device=test_device)

net.load(model_path)

if not os.path.exists(result_path):
    os.makedirs(result_path)

namedWindow("Win0", WINDOW_AUTOSIZE);
namedWindow("Win1", WINDOW_AUTOSIZE);
namedWindow("Win2", WINDOW_AUTOSIZE);
namedWindow("Win3", WINDOW_AUTOSIZE);

cam = VideoCapture(0)
while(True):
    s, img = cam.read()
    if s:    # frame captured without any errors
        orig_image = cv2.resize(img, (640, 480));

        image = cv2.cvtColor(orig_image, cv2.COLOR_BGR2RGB)
        boxes, labels, probs = predictor.predict(image, args.candidate_size / 2, args.threshold)
        for i in range(boxes.size(0)):
            box = boxes[i, :]
            label = f"{probs[i]:.2f}"
            cv2.putText(orig_image, str(boxes.size(0)), (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cropped = orig_image[int(box[1]):int(box[3]), int(box[0]):int(box[2])]
            try:
                imshow("Win" + str(i), cropped);
            except:
                print("Img capture error");
            waitKey(1);
            cv2.imwrite('./results/new' + str(i) + '.jpg', cropped)
        print(f"Found {len(probs)} faces.")

    time.sleep(0.5);
