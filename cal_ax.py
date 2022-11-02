import argparse
import re
import os
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('dir_num', type=str)
arg = parser.parse_args()
result_dir = arg.dir_num

print("좌표 계산중")

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]

roi = os.path.join(result_dir, 'roi.txt')
yolo = os.path.join(result_dir, 'person_box.txt')

roi_f = open(roi)
yolo_f = open(yolo)

roi_data = roi_f.readlines()
yolo_data = yolo_f.readlines()

#yolo_num = re.findall("\d+", yolo_data[150])

"""
print(roi_num) # yxyx
print(yolo_num) # xyxy
"""
def box_area(a1, a2, b1, b2):
    return (a2 - a1) * (b2 - b1)

def cal_box_percent(x1, x2, y1, y2, a1, a2, b1, b2):
    if (a1 < x1) and (a2 < x2):   #1 4 7
        if (b1 > y1) and (b2 < y2): #1
            return (a2 - x1)*(b2 - y1)
        elif b1 >= y1:
            if b2 <= y2: #4
                return (a2 - x1)*(b2 - b1)
            elif b2 > y2:   #7
                return (a2 - x1)*(y2 - b1)
    elif (a1 >= x1) and (a2 <= x2):   # 2 5 8
        if (b1 < y1) and (b2 < y2):   #2
            return (a2 - a1)*(b2 - y1)
        elif b1 >= y1:
            if b2 <= y2: #5
                return 0 #(a2 - a1)*(b2 - b1)
            elif b2 > y2:   #8
                return (a2 - a1)*(y2 - b1)
    elif (a1 > x1) and (a2 > x2):   # 3 6 9
        if (b1 < y1) and (b2 > y1):   #3
            return (x2 - a1)*(b2 - y1)
        elif b1 > y1:
            if b2 <= y2: #6
                return (x2 - a1)*(b2 - b1)
            elif b2 > y2:   #9
                return (x2 - a1)*(y2 - b1)
    return 0

print(len(roi_data))
print(len(yolo_data))

warn_cnt = 0
danger_cnt = 0
cnt = 0
box_percent = 0
box_percent_sum = 0

for temp1, temp2 in zip(yolo_data, roi_data):
    roi_num = re.findall("\d+", temp2)
    i = 2
    cnt += 1
    check_status = True
    yolo_num = re.findall("\d+", temp1)
    if 'personINthewater' in temp1:
        danger_cnt = danger_cnt + 1
    else:
        if len(yolo_num) > 1:
            river_x1 = int(roi_num[1])
            river_y1 = int(roi_num[0])
            river_x2 = int(roi_num[3])
            river_y2 = int(roi_num[2])
            while len(yolo_num) > (i - 2):
                person_x1 = int(yolo_num[0 + i])
                person_y1 = int(yolo_num[1 + i])
                person_x2 = int(yolo_num[2 + i])
                person_y2 = int(yolo_num[3 + i])
                if len(yolo_num) > (i - 2):
                    i = i + 6
                else:
                    break
                if (person_x1 >= river_x1) and (person_y1 >= river_y1) and (person_x2 <= river_x2) and (person_y2 <= river_y2):
                    danger_cnt += 1
                    break
                else:
                    if (person_x1 >= river_x1) and (person_x1 <= river_x2):
                        if (person_y1 >= river_y1) and (person_y1 <= river_y2):
                            warn_cnt += 1
                            box_num = cal_box_percent(river_x1, river_x2, river_y1, river_y2, person_x1, person_x2, person_y1, person_y2)
                            box_area_num = box_area(person_x1, person_x2, person_y1, person_y2)
                            box_percent = float(box_num) / float(box_area_num)
                            box_percent_sum = box_percent_sum + box_percent
                            print("1 = " + str(box_num) + " " + str(box_area_num) + " " + str(box_percent) + " " + str(box_percent_sum))
                            break
                    elif (person_x2 >= river_x1) and (person_x2 <= river_x2):
                        if (person_y2 >= river_y1) and (person_y2 <= river_y2):
                            warn_cnt += 1
                            box_num = cal_box_percent(river_x1, river_x2, river_y1, river_y2, person_x1, person_x2, person_y1, person_y2)
                            box_area_num = box_area(person_x1, person_x2, person_y1, person_y2)
                            box_percent = float(box_num) / float(box_area_num)
                            box_percent_sum = box_percent_sum + box_percent
                            print("2 = " + str(box_num) + " " + str(box_area_num) + " " + str(box_percent) + " " + str(box_percent_sum))
                            break


box_percent_avg = box_percent_sum / warn_cnt * 100

#print(yolo_num)
"""
for temp in yolo_data:
    temp_num = re.findall("\d+", temp)
    cnt += 1
    if len(temp_num) > 1:
        person_x1 = int(temp_num[0])
        person_y1 = int(temp_num[1])
        person_x2 = int(temp_num[2])
        person_y2 = int(temp_num[3])
        if (person_x1 >= roi_x1) and (person_y1 >= roi_y1) and (person_x2 <= roi_x2) and (person_y2 <= roi_y2):
            danger_cnt += 1
        else:
            if (person_x1 >= roi_x1) and (person_x1 <= roi_x2):
                if (person_y1 >= roi_y1) and (person_y1 <= roi_y2):
                    warn_cnt += 1
            elif (person_x2 >= roi_x1) and (person_x2 <= roi_x2):
                if (person_y2 >= roi_y1) and (person_y2 <= roi_y2):
                    warn_cnt += 1
"""
with open(os.path.join(result_dir, 'status.txt'), 'w') as status_f:
    status_f.write("경고 프레임 수 = " + str(warn_cnt) + "\n")
    status_f.write("위험 프레임 수 = " + str(danger_cnt) + "\n")
    status_f.write("강 접근 장면 평균 = " + str(box_percent_avg) + "%\n")

print("좌표 계산 완료")
roi_f.close()
yolo_f.close()
