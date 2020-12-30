from django.shortcuts import render

# Create your views here.
from django.http.response import StreamingHttpResponse
from django.db import transaction
from picture.models import Picture,Statstics

import json
import cv2
import tensorflow as tf
from .utils.utils import get_yolo_boxes
from tensorflow.keras.models import load_model
from .object_tracking.deep_sort import nn_matching
from .object_tracking.deep_sort.detection import Detection
from .object_tracking.deep_sort.tracker import Tracker
from .object_tracking.application_util import generate_detections as gdet
from .utils.bbox import draw_box_with_id
import os
from api.settings import BASE_DIR


file_path = os.path.join(BASE_DIR, 'relative_path')

from datetime import datetime
import datetime as dt

import warnings

warnings.filterwarnings("ignore")


# import winsound


config = tf.ConfigProto()
config.gpu_options.allow_growth = True
tf.keras.backend.set_session(tf.Session(config=config))

"""DISPLAY CAMERA"""


def stream():
    config_path = 'webcam/config.json'
    num_cam = 1
    with open(config_path) as config_buffer:
        config = json.load(config_buffer)

    net_h, net_w = 416, 416  # a multiple of 32, the smaller the faster
    obj_thresh, nms_thresh = 0.5, 0.45

    os.environ['CUDA_VISIBLE_DEVICES'] = config['train']['gpus']
    infer_model = load_model(config['train']['saved_weights_name'])

    max_cosine_distance = 0.3
    nn_budget = None

    model_filename = 'webcam/mars-small128.pb'
    encoder = gdet.create_box_encoder(model_filename, batch_size=1)

    trackers = []
    for i in range(num_cam):
        metric = nn_matching.NearestNeighborDistanceMetric("cosine", max_cosine_distance, nn_budget)
        tracker = Tracker(metric)
        trackers.append(tracker)

    video_readers = []
    for i in range(num_cam):
        video_reader = cv2.VideoCapture(i)
        video_readers.append(video_reader)

    # the main loop
    batch_size = num_cam
    images = []

    no_helmet_time = 0
    duration = 2000  # milliseconds
    freq = 880  # Hz

    today_no_helmet_count = 0
    current_date = dt.datetime.now()
    current_date = current_date.strftime('%Y-%m-%d')



    while True:
        for i in range(num_cam):
            ret_val, image = video_readers[i].read()
            if ret_val == True: images += [image]

        if (len(images) == batch_size) or (ret_val == False and len(images) > 0):

            batch_boxes = get_yolo_boxes(infer_model, images, net_h, net_w, config['model']['anchors'], obj_thresh,
                                         nms_thresh)

            for i in range(len(images)):
                boxs = [[box1.xmin, box1.ymin, box1.xmax - box1.xmin, box1.ymax - box1.ymin] for box1 in batch_boxes[i]]
                features = encoder(images[i], boxs)

                # print(features)
                # score to 1.0 here).
                detections = []
                for j in range(len(boxs)):
                    label = batch_boxes[i][j].label
                    detections.append(Detection(boxs[j], batch_boxes[i][j].c, features[j], label))

                # Call the tracker
                trackers[i].predict()
                trackers[i].update(detections)

                n_without_helmet = 0
                n_with_helmet = 0

                for track in trackers[i].tracks:
                    if not track.is_confirmed() or track.time_since_update > 1:
                        continue
                    if track.label == 2:
                        n_without_helmet += 1
                    if track.label == 1:
                        n_with_helmet += 1
                    bbox = track.to_tlbr()
                    # print(track.track_id,"+",track.label)
                    draw_box_with_id(images[i], bbox, track.track_id, track.label, config['model']['labels'])

                # for det in detections:
                #     print(det.label)
                #     bbox = det.to_tlbr()
                #     cv2.rectangle(images[i], (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (255, 0, 0), 2)

                print("CAM " + str(i))
                print("Persons without helmet = " + str(n_without_helmet))
                print("Persons with helmet = " + str(n_with_helmet))
                # cv2.imshow('Cam' + str(i), images[i])
                cv2.imwrite('demo.jpg', images[i])

                if n_without_helmet >= 1:
                    filename = datetime.today().strftime("%Y%m%d%H%M%S")
                    cv2.imwrite('picture/{}.jpg'.format(filename), images[i])
                    with transaction.atomic():
                        picture = Picture(picture_name=filename)
                        picture.save()
                        if Statstics.objects.filter(created_date=current_date).exists():
                            statistic = Statstics.objects.get(created_date=current_date)
                        else:
                            statistic = Statstics(created_date = current_date)
                        statistic.count += 1
                        statistic.save()


                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + open('demo.jpg', 'rb').read() + b'\r\n')

                """
                if(n_without_helmet):
                """

                if n_without_helmet > 0:
                    no_helmet_time += 1
                else:
                    # 여기서 오늘 하루 모자를 몇번 벗었는지 카운팅 해야함
                    today_no_helmet_count += 1
                    no_helmet_time = 0

                print("no_helmet_time : " + str(no_helmet_time))
                if no_helmet_time >= 10:
                    # winsound.Beep(freq ,duration)
                    no_helmet_time -= 2

            # ret, jpeg = cv2.imencode('.jpg', images[i])
            # frame = jpeg.tobytes()
            # cv2.imwrite('demo.jpg', frame)
            # yield (b'--frame\r\n'
            #	   b'Content-Type: image/jpeg\r\n\r\n' + open('demo.jpg', 'rb').read() + b'\r\n')
            images = []


"""FEED VIDEO"""


def video_feed_1(request):
    return StreamingHttpResponse(stream(), content_type='multipart/x-mixed-replace; boundary=frame')