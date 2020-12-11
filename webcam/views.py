from django.shortcuts import render


from django.http.response import StreamingHttpResponse


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


import warnings
warnings.filterwarnings("ignore")


config = tf.ConfigProto()
config.gpu_options.allow_growth = True
tf.keras.backend.set_session(tf.Session(config=config))


def stream():
	config_path = 'webcam/config.json'
	num_cam = 1
	with open(config_path) as config_buffer:
		config = json.load(config_buffer)

	net_h, net_w = 416, 416  
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

				
				# score to 1.0 here).
				detections = []
				for j in range(len(boxs)):
					label = batch_boxes[i][j].label
					detections.append(Detection(boxs[j], batch_boxes[i][j].c, features[j], label))

				# Call the tracker
				trackers[i].predict()
				trackers[i].update(detections)


				for track in trackers[i].tracks:
					if not track.is_confirmed() or track.time_since_update > 1:
						continue
					if track.label == 2:
						n_without_helmet += 1
					if track.label == 1:
						n_with_helmet += 1
					bbox = track.to_tlbr()
					draw_box_with_id(images[i], bbox, track.track_id, track.label, config['model']['labels'])


			images = []



def video_feed_1(request):
    return StreamingHttpResponse(stream(), content_type='multipart/x-mixed-replace; boundary=frame')

