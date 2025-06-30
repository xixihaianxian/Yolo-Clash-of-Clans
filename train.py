from ultralytics import YOLO

if __name__=="__main__":

    yolov10=YOLO("yolov10x.yaml").load("./yolov10x.pt") #TODO 加载预训练模型

    yolov10.train(
        data="./data.yaml",
        epochs=20,
        imgsz=640,
        batch=16,
        device="cuda",
        save=True,
    ) #TODO 训练

    metrics=yolov10.val(
        data="./data.yaml"
    ) #TODO 验证

    print(metrics) #TODO 打印验证结果