from ultralytics import YOLO
import torch
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import config
import os
import random
import numpy as np

def anchor_transform(anchor): #TODO 转化yolo模型生成的xywh
    left = anchor[0] - anchor[2] / 2
    top = anchor[1] - anchor[3] / 2
    width = anchor[2]
    height = anchor[3]
    return left,top,width,height

def choice_image(dir): #TODO 随机选择一张test里面的图片
    img_dir=os.path.join(dir,"images")
    img_list=os.listdir(img_dir)
    img_name=random.choice(img_list)
    img_file=os.path.join(img_dir,img_name)
    return img_file

def draw_anchor_box(axes,anchors,image,labels,is_predict=True): #TODO 绘制锚框
    # plt.figure()
    # fig=plt.imshow(image)
    axes.imshow(image)
    if isinstance(anchors,torch.Tensor):
        anchors=anchors.cpu()
    for anchor,label in zip(anchors,labels):
        if is_predict:
            left, top, width, height=anchor_transform(anchor)
        axes.axes.add_patch(p=Rectangle(
            xy=(left,top),
            width=width,
            height=height,
            linewidth=1.5,
            fill=False,
            edgecolor=config.color_dict.get(label)
        ))
        axes.axes.text(
            x=left,
            y=top,
            s=label,
            va="center",
            ha="center",
            fontsize=6,
            fontweight=500,
            color=config.color_dict.get(label)
        )
    # plt.savefig(os.path.join("./result","result.png"))
    # plt.show()
    
def actual_anchor_label(img_file,dir,orig_weight,orig_height,id2name): #TODO 获取实际的锚框和标签
    
    label_name=os.path.splitext(os.path.basename(img_file))[0]+".txt"
    label_file=os.path.join(dir,"labels",label_name)
    
    with open(label_file,"r",encoding="utf-8") as file:
        labels_anchors=list(map(lambda item:item.strip("\n").split(" "),file.readlines()))
        
    labels=list(map(lambda item:int(item[0]),labels_anchors))
    anchors=list(map(lambda item:[item[1],item[2],item[3],item[4]],labels_anchors))
    anchors=np.array(anchors,dtype=np.float32)
    orig=np.array([orig_weight,orig_height,orig_weight,orig_height],dtype=np.float32)
    anchors=anchors*orig
    labels=list(map(lambda item:id2name.get(item),labels))
    
    return anchors,labels
    
def compare_actual_predict(image,actual_anchors,actual_labels,predict_anchors,predict_labels,save_name=None):
    r'''
    使用真实的结果和预测的结果进行对比
    '''
    os.path.exists("./result") or os.makedirs("./result")
    plt.figure()
    
    axes_1=plt.subplot(1,2,1)
    draw_anchor_box(axes_1,actual_anchors,image,actual_labels)
    axes_1.set_title("actual")
    axes_1.set_yticks([])
    axes_1.set_xticks([])
    
    axes_2=plt.subplot(1,2,2)
    draw_anchor_box(axes_2,predict_anchors,image,predict_labels)
    axes_2.set_title("predict")
    axes_2.set_xticks([])
    axes_2.set_yticks([])
    
    if save_name is None:
        plt.savefig("./result/result.png")
    else:
        plt.savefig(f"./result/{save_name}.png")
    
    plt.show()

if __name__=="__main__":

    yolov10=YOLO(config.BEST_WEIGHT) #TODO 获取最佳的模型

    img_file=choice_image(config.TEST_FILE)

    result=yolov10.predict(img_file)

    predict_anchors=result[0].boxes.xywh  #TODO 获取预测的锚框

    id2name=result[0].names

    ids=result[0].boxes.cls

    predict_labels=[id2name.get(id.to(dtype=torch.int64).item()) for id in ids] #TODO 获取预测的标签

    image=result[0].orig_img #TODO 原始图片
    
    orig_weight,orig_height=result[0].orig_shape
    
    # draw_anchor_box(anchors,image, labels)
    
    actual_anchors,actual_labels=actual_anchor_label(img_file=img_file,dir=config.TEST_FILE,orig_weight=orig_weight,
                                                 orig_height=orig_height,id2name=id2name)
    
    save_name=os.path.splitext(os.path.basename(img_file))[0]
    
    compare_actual_predict(image=image,actual_anchors=actual_anchors,actual_labels=actual_labels,
                           predict_anchors=predict_anchors,predict_labels=predict_labels,save_name=save_name)