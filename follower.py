import cv2
import numpy as np
from PIL import Image
import time
from threading import Thread
import sys
import serial
import hailo
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import os
import argparse
import multiprocessing
import setproctitle
import cv2
import time
from hailo_rpi_common import (
    get_default_parser,
    QUEUE,
    get_caps_from_pad,
    get_numpy_from_buffer,
    GStreamerApp,
    app_callback_class,
)


#------------------------------------------------------------------------------------------------
#Variables
#------------------------------------------------------------------------------------------------
global x_deviation, y_max, tolerance

object_to_track = "person"
tolerance = 0.1

USB_PORT = "/dev/ttyAMA0"

# -----------------------------------------------------------------------------------------------
# User-Defined functions
# -----------------------------------------------------------------------------------------------
# Inheritance from the app_callback_class
class user_app_callback_class(app_callback_class):
    def __init__(self):
        super().__init__()
    
    def move_back():
        # print("Moving Back")
        ser.write(b"backward\n")
        line = ser.readline().decode('utf-8').rstrip()
        print(line)

    def move_forward():
        # print("Moving forward")
        ser.write(b"forward\n")
        line = ser.readline().decode('utf-8').rstrip()
        print(line)

    def move_right():
        # print("Moving right")
        ser.write(b"right\n")
        line = ser.readline().decode('utf-8').rstrip()
        print(line)

    def move_left():
        # print("Moving left")
        ser.write(b"left\n")
        line = ser.readline().decode('utf-8').rstrip()
        print(line)

    def stop():
        # print("STOP")
        ser.write(b"stop\n")
        line = ser.readline().decode('utf-8').rstrip()
        print(line)


    def move_robot(y_max, x_deviation):
        y = 1 - y_max
        print(y_max)
        print(y)
        if (abs(x_deviation) < tolerance):
            if (y < 0.25):
                user_app_callback_class.stop()
                
            else:
                user_app_callback_class.move_forward()
        
        else:
            if(x_deviation >= tolerance):
                delay = user_app_callback_class.get_delay(x_deviation)
                user_app_callback_class.move_left()
                time.sleep(delay)
                user_app_callback_class.stop()
            
            if(x_deviation<=-1*tolerance):
                delay = user_app_callback_class.get_delay(x_deviation)
                user_app_callback_class.move_right()
                time.sleep(delay)
                user_app_callback_class.stop()

    def get_delay(deviation):
        deviation = abs(deviation)
        if(deviation>=0.4):
            d=0.080
        elif(deviation>=0.35 and deviation<0.40):
            d=0.060
        elif(deviation>=0.20 and deviation<0.35):
            d=0.050
        else:
            d=0.040
        
        return d

# -----------------------------------------------------------------------------------------------
# User-defined callback function
# -----------------------------------------------------------------------------------------------
def app_callback(pad, info, user_data):
    # Get the GstBuffer from the probe info
    buffer = info.get_buffer()
    # Check if the buffer is valid
    if buffer is None:
        return Gst.PadProbeReturn.OK
        
    # Using the user_data to count the number of frames
    user_data.increment()
    string_to_print = f"Frame count: {user_data.get_count()}\n"
    
    # Get the caps from the pad
    format, width, height = get_caps_from_pad(pad)

    # If the user_data.use_frame is set to True, we can get the video frame from the buffer
    frame = None
    if user_data.use_frame and format is not None and width is not None and height is not None:
        # Get video frame
        frame = get_numpy_from_buffer(buffer, format, width, height)

    # Get the detections from the buffer
    roi = hailo.get_roi_from_buffer(buffer)
    detections = roi.get_objects_typed(hailo.HAILO_DETECTION)

    # Parse the detections
    detection_count = 0
    for detection in detections:
        label = detection.get_label()
        bbox = detection.get_bbox()
        confidence = detection.get_confidence()
        if label == object_to_track:
            string_to_print += f"Detection: {label} {confidence:.2f}\n"

            x_max = bbox.xmax()
            x_min = bbox.xmin()

            y_max = bbox.ymax()
            y_min = bbox.ymin()

            x_diff = x_max - x_min
            y_diff = y_max - y_min

            obj_x_center = x_min + (x_diff / 2)
            obj_x_center = round(obj_x_center, 3)

            obj_y_center = y_min + (y_diff / 2)
            obj_y_center = round(obj_y_center, 3)
            
            x_deviation = round(0.5 - obj_x_center, 3)
            y_max = round(y_max, 3)

            print("{",x_deviation,y_max,"}")
            
            user_app_callback_class.move_robot(y_max, x_deviation)


            detection_count += 1

    print(string_to_print)
    return Gst.PadProbeReturn.OK

# -----------------------------------------------------------------------------------------------
# User Gstreamer Application
# -----------------------------------------------------------------------------------------------

# This class inherits from the hailo_rpi_common.GStreamerApp class
class GStreamerDetectionApp(GStreamerApp):
    def __init__(self, args, user_data):
        # Call the parent class constructor
        super().__init__(args, user_data)
        # Additional initialization code can be added here
        # Set Hailo parameters these parameters should be set based on the model used
        self.batch_size = 2
        self.network_width = 640
        self.network_height = 640
        self.network_format = "RGB"
        nms_score_threshold = 0.3 
        nms_iou_threshold = 0.45
        
        new_postprocess_path = os.path.join(self.current_path, './resources/libyolo_hailortpp_post.so')
        if os.path.exists(new_postprocess_path):
            self.default_postprocess_so = new_postprocess_path
        else:
            self.default_postprocess_so = os.path.join(self.postprocess_dir, 'libyolo_hailortpp_post.so')

        if args.hef_path is not None:
            self.hef_path = args.hef_path
        # Set the HEF file path based on the network
        elif args.network == "yolov6n":
            self.hef_path = os.path.join(self.current_path, './resources/yolov6n.hef')
        elif args.network == "yolov8s":
            self.hef_path = os.path.join(self.current_path, './resources/yolov8s_h8l.hef')
        elif args.network == "yolox_s_leaky":
            self.hef_path = os.path.join(self.current_path, './resources/yolox_s_leaky_h8l_mz.hef')
        else:
            assert False, "Invalid network type"

        # User-defined label JSON file
        if args.labels_json is not None:
            self.labels_config = f' config-path={args.labels_json} '
            # Temporary code
            if not os.path.exists(new_postprocess_path):
                print("New postprocess so file is missing. It is required to support custom labels. Check documentation for more information.")
                exit(1)
        else:
            self.labels_config = ''

        self.app_callback = app_callback
    
        self.thresholds_str = (
            f"nms-score-threshold={nms_score_threshold} "
            f"nms-iou-threshold={nms_iou_threshold} "
            f"output-format-type=HAILO_FORMAT_TYPE_FLOAT32"
        )

        # Set the process title
        setproctitle.setproctitle("Hailo Detection App")

        self.create_pipeline()

    def get_pipeline_string(self):
        if self.source_type == "rpi":
            source_element = (
                "libcamerasrc name=src_0 auto-focus-mode=2 ! "
                f"video/x-raw, format={self.network_format}, width=1536, height=864 ! "
                + QUEUE("queue_src_scale")
                + "videoscale ! "
                f"video/x-raw, format={self.network_format}, width={self.network_width}, height={self.network_height}, framerate=10/1 ! "
            )
        elif self.source_type == "usb":
            source_element = (
                f"v4l2src device={self.video_source} name=src_0 ! "
                "video/x-raw, width=640, height=480, framerate=30/1 ! "
            )
        else:
            source_element = (
                f"filesrc location={self.video_source} name=src_0 ! "
                + QUEUE("queue_dec264")
                + " qtdemux ! h264parse ! avdec_h264 max-threads=2 ! "
                " video/x-raw, format=I420 ! "
            )
        source_element += QUEUE("queue_scale")
        source_element += "videoscale n-threads=2 ! "
        source_element += QUEUE("queue_src_convert")
        source_element += "videoconvert n-threads=3 name=src_convert qos=false ! "
        source_element += f"video/x-raw, format={self.network_format}, width={self.network_width}, height={self.network_height}, pixel-aspect-ratio=1/1 ! "

        pipeline_string = (
            "hailomuxer name=hmux "
            + source_element
            + "tee name=t ! "
            + QUEUE("bypass_queue", max_size_buffers=20)
            + "hmux.sink_0 "
            + "t. ! "
            + QUEUE("queue_hailonet")
            + "videoconvert n-threads=3 ! "
            f"hailonet hef-path={self.hef_path} batch-size={self.batch_size} {self.thresholds_str} force-writable=true ! "
            + QUEUE("queue_hailofilter")
            + f"hailofilter so-path={self.default_postprocess_so} {self.labels_config} qos=false ! "
            + QUEUE("queue_hmuc")
            + "hmux.sink_1 "
            + "hmux. ! "
            + QUEUE("queue_hailo_python")
            + QUEUE("queue_user_callback")
            + "identity name=identity_callback ! "
            + QUEUE("queue_hailooverlay")
            + "hailooverlay ! "
            + QUEUE("queue_videoconvert")
            + "videoconvert n-threads=3 qos=false ! "
            + QUEUE("queue_hailo_display")
            + f"fpsdisplaysink video-sink={self.video_sink} name=hailo_display sync={self.sync} text-overlay={self.options_menu.show_fps} signal-fps-measurements=true "
        )
        print(pipeline_string)
        return pipeline_string

if __name__ == "__main__":
    user_data = user_app_callback_class()
    parser = get_default_parser()
    parser.add_argument(
        "--network",
        default="yolov8s",
        choices=['yolov6n', 'yolov8s', 'yolox_s_leaky'],
        help="Which Network to use, default is yolov6n",
    )
    parser.add_argument(
        "--hef-path",
        default=None,
        help="Path to HEF file",
    )
    parser.add_argument(
        "--labels-json",
        default=None,
        help="Path to costume labels JSON file",
    )

    try:
        ser = serial.Serial(USB_PORT, 9600, timeout= 2)
    except:
        print("ERROR - could not open USB serial port. Please check your port name and permissions.")
        print("Exiting program.")
        exit()
    

    print("Please choose operating type:")
    print("1 = Autonomous")
    print("2 = Follower")

    operatingType = input("Chosen Operating Type: ")

    if operatingType == 1:
        ser.write(b"auto\n")
    
    elif operatingType == 2:
        ser.write(b"follow\n")
        args = parser.parse_args()
        app = GStreamerDetectionApp(args, user_data)
        app.run()
    
    else:
        print("Wrong type, please input 1 or 2 to choose operating type")