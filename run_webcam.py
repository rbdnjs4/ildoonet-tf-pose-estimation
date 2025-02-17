from abc import abstractmethod
import argparse
import logging
import time
from pprint import pprint
import cv2
import numpy as np
import time
import sys
from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path, model_wh
import math
from playsound import playsound
from tf_pose import common

logger = logging.getLogger('TfPoseEstimator-WebCam')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
global result_x, result_y
fps_time = 0
start = 0
end = 0
def find_point_neck(pose, p):
    for point in pose:
        try:
            body_part = point.body_parts[p]
            return int(body_part.y * height + 0.5)
        except:
            return (0)
    return (0)

def find_point_ear(pose, p):
    for point in pose:
        try:
            body_part = point.body_parts[p]
            return int(body_part.y * height + 0.5)
        except:
            return (0)
    return (0)   

def find_point(pose, p):
    for point in pose:
        try:
            body_part = point.body_parts[p]
            return (int(body_part.x * width + 0.5), int(body_part.y * height + 0.5))
        except:
            return (0,0)
    return (0,0)

def euclidian( point1, point2):
    return math.sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2 )

def angle_calc(p0, p1, p2 ):
    try:
        a = (p1[0]-p0[0])**2 + (p1[1]-p0[1])**2
        b = (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2
        c = (p2[0]-p0[0])**2 + (p2[1]-p0[1])**2
        angle = math.acos( (a+b-c) / math.sqrt(4*a*b) ) * 180/math.pi
    except:
        return 0
    return int(angle)
    
def plank( a, b, c, d, e, f):
    #There are ranges of angle and distance to for plank. 
    '''
        a and b are angles of hands
        c and d are angle of legs
        e and f are distance between head to ankle because in plank distace will be maximum.
    '''
    if (a in range(50,100) or b in range(50,100)) and (c in range(135,175) or d in range(135,175)) and (e in range(50,250) or f in range(50,250)):
        return True
    return False

def turtleneck_pose(a,b) :
    if a in range(0,70) and b in range(15, 90):
        return True
    return False

def draw_str(dst, xxx_todo_changeme, s, color, scale):
    
    (x, y) = xxx_todo_changeme
    if (color[0]+color[1]+color[2]==255*3):
        cv2.putText(dst, s, (x+1, y+1), cv2.FONT_HERSHEY_PLAIN, scale, (1, 0, 255), thickness = 4, lineType=5)
    else:
        cv2.putText(dst, s, (x+1, y+1), cv2.FONT_HERSHEY_PLAIN, scale, color, thickness = 4, lineType=5)
    #cv2.line    
    cv2.putText(dst, s, (x, y), cv2.FONT_HERSHEY_PLAIN, scale, (1, 0, 255), lineType=11)
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='tf-pose-estimation realtime webcam')
    parser.add_argument('--camera', type=str, default=0)
    parser.add_argument('--resize', type=str, default='432x368',
                        help='if provided, resize images before they are processed. default=432x368, Recommends : 432x368 or 656x368 or 1312x736 ')
    parser.add_argument('--resize-out-ratio', type=float, default=4.0,
                        help='if provided, resize heatmaps before they are post-processed. default=1.0')

    parser.add_argument('--model', type=str, default='cmu', help='cmu / mobilenet_thin')
    parser.add_argument('--show-process', type=bool, default=False,
                        help='for debug purpose, if enabled, speed for inference is dropped.')
    args = parser.parse_args()
    
    logger.debug('initialization %s : %s' % (args.model, get_graph_path(args.model)))
    w, h = model_wh(args.resize)
    if w > 0 and h > 0:
        e = TfPoseEstimator(get_graph_path(args.model), target_size=(w, h))
    else:
        e = TfPoseEstimator(get_graph_path(args.model), target_size=(432, 368))
    logger.debug('cam read+')
    cam = cv2.VideoCapture(args.camera)
    ret_val, image = cam.read()
    logger.info('cam image=%dx%d' % (image.shape[1], image.shape[0]))
    count = 0
    i = 0
    frm = 0
    y1 = [0,0]
    global height,width
    red_color = (1,0,255)
    while True:
        ret_val, image = cam.read()
        i =1
        humans = e.inference(image, resize_to_default=(w > 0 and h > 0), upsample_size=args.resize_out_ratio)
        pose = humans
        image = TfPoseEstimator.draw_humans(image, humans, imgcopy=False)
        height,width = image.shape[0],image.shape[1]

        

        no_people = len(humans) #사람 수 입력
        print("people : ", int(no_people))
        if(no_people == 1) : #사람이 한 명일때만 인식
                # cv2.putText(image,
                #             "People: %f" % no_people,
                #             (10, 50),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                #             (255, 255, 255), 2)
                # cv2.putText(image,
                #         "nose : {}, neck : {}, ear : {}".format(find_point(pose,0),find_point(pose,1),find_point(pose,17)),
                #         (10, 90),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                #         (255, 255, 255), 2)
            a = find_point(pose,0) #코
            b = find_point(pose,1) #귀
                
            if len(pose) > 0:
                #17귀, 0코, 1목, 
                # if find_point(pose,1):
                if a[0] < b[0]: #왼쪽 측면
                        # cv2.line(image, (0,find_point_neck(pose,1)), find_point(pose,1), common.CocoColors[3], 3)
                        # cv2.line(image, find_point(pose,17), find_point(pose,1), common.CocoColors[3], 3)
                        # cv2.line(image, find_point(pose,17), find_point(pose,0), common.CocoColors[3], 3)
                        # cv2.line(image, (0,find_point_neck(pose,1)), find_point(pose,0), common.CocoColors[3], 3)

                        
                    cv2.putText(image,
                        "LEFT",
                        (350, 10),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (255, 255, 255), 2)
                    angle1 =  angle_calc((0,find_point_neck(pose,1)),find_point(pose,1),find_point(pose,17))
                    angle2 =  angle_calc(find_point(pose,0),(0,find_point_neck(pose,1)),find_point(pose,1))

                    #18귀, 0코, 1목
                elif a[0] > b[0]: #오른쪽 측면
                    cv2.putText(image,
                        "RIGHT",
                        (350, 10),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (255, 255, 255), 2)
                        # cv2.line(image, (720,find_point_neck(pose,1)), find_point(pose,1), common.CocoColors[3], 3)
                        # cv2.line(image, find_point(pose,16), find_point(pose,1), common.CocoColors[3], 3)
                        # cv2.line(image, find_point(pose,16), find_point(pose,0), common.CocoColors[3], 3)
                        # cv2.line(image, (720,find_point_neck(pose,1)), find_point(pose,0), common.CocoColors[3], 3)

                    angle1 =  angle_calc((720,find_point_neck(pose,1)),find_point(pose,1),find_point(pose,16))
                    angle2 =  angle_calc(find_point(pose,0),(720,find_point_neck(pose,1)),find_point(pose,1))
                    # cv2.putText(image,
                    #     "nose to neck : {}, ear to neck : {}".format(angle1,angle2),
                    #     (10, 110),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    #     (255, 255, 255), 2)

                    
                    
                if turtleneck_pose(angle1, angle2) == True:
                    start = start + 1 #약 7프레임 가량 거북목이 유지돼야 거북목이라 인식 됨
                    cv2.putText(image,
                        "count = {}".format(start),
                        (10, 110),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (255, 255, 255), 2)
                    if turtleneck_pose(angle1, angle2) == True and start > 6:
                        action = "Turtle neck!!!"
                        draw_str(image, (280, 30), action, red_color, 2)
                        playsound("turtle.wav") #거북목이라 인식되면 경보
                else:
                    start = 0 #7초간 프레임이 유지되지 않는다면 거북목이 아니라 판단
            
                    # logger.debug("Turtle neck!!!!!!!")
                    # playsound("soundtest.wav")
        # elif (mode == 3):
        #     no_people = len(humans)
        #     print("no. of people : ", no_people)
        #     cv2.putText(image,
        #                 "People: %f" % no_people,
        #                 (10, 50),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,
        #                 (255, 255, 255), 2)
        #     cv2.putText(image,
        #             "People: {}".format(common.CocoColors[1]),
        #             (10, 70),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,
        #             (255, 255, 255), 2)
        #     cv2.putText(image,
        #             "x : {}, y : {}".format((0,find_point_neck(pose,1)),find_point(pose,1)),
        #             (10, 90),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,
        #             (255, 255, 255), 2)

            
        #     if len(pose) > 0:

        #         if find_point(pose,1):
        #             cv2.line(image, (0,find_point_neck(pose,1)), find_point(pose,1), common.CocoColors[3], 3)

        #         # distance calculations
        #         head_hand_dst_l = int(euclidian(find_point(pose, 0), find_point(pose, 7)))
        #         head_hand_dst_r = int(euclidian(find_point(pose, 0), find_point(pose, 4)))
        #         m_pose = int( euclidian(find_point(pose, 7), find_point(pose, 4)))
                
        #         # angle calcucations
        #         angle1 =  angle_calc(find_point(pose, 6), find_point(pose, 5), find_point(pose, 1))
        #         angle5 =  angle_calc(find_point(pose,3), find_point(pose,2), find_point(pose,1))
                
        #         logger.debug(angle1)
        #         if (mode == 3) and mountain_pose(m_pose, angle1, angle5, head_hand_dst_r, head_hand_dst_l):
        #                     # draw_str(frame, (20, 220), " Mountain Pose", orange_color, 1.5)
        #                     action = "Mountain Pose"
        #                     is_yoga = True
        #                     #if prev_action == 'Unknown' or prev_action == "Unknown_First":
        #                     #    yoga_duration = time.time()
        #                     draw_str(image, (10, 50), action, orange_color, 2)
        #                     logger.debug("Turtle neck!!!!!!!")
        #                     playsound("soundtest.wav")
        cv2.putText(image,
                    "FPS: %f" % (1.0 / (time.time() - fps_time)),
                    (10, 10),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 255, 0), 2)
        #image =   cv2.resize(image, (720,720))
        if(frm==0):
            out = cv2.VideoWriter('outpy.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 30, (image.shape[1],image.shape[0]))
            print("Initializing")
            frm+=1
        cv2.imshow('tf-pose-estimation result', image)
        if i != 0:
            out.write(image)
        fps_time = time.time()
        if cv2.waitKey(1) == 27:
            break

    cv2.destroyAllWindows()