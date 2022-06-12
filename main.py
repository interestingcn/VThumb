import os,time,av
from PIL import Image, ImageFont, ImageDraw
from multiprocessing import Pool

import warnings
warnings.filterwarnings("ignore")

IMAGE_PER_ROW = 4   # 横向 列
IMAGE_ROWS = 5      # 纵向 行
PADDING = 5
FONT_SIZE = 19
IMAGE_WIDTH = 1920
FONT_NAME = "simhei.ttf"
BACKGROUND_COLOR = "#fff"
TEXT_COLOR = "#000"
TIMESTAMP_COLOR = "#fff"

def welcome():
    msg = '''_   _ _____ _                     _     
| | | |_   _| |批量视频略缩图生成工具 | |    
| | | | | | | |__  _   _ _ __ ___ | |__  
| | | | | | | '_ \| | | | '_ ` _ \| '_ \ 
\ \_/ / | | | | | | |_| | | | | | | |_) |
 \___/  \_/ |_| |_|\__,_|_| |_| |_|_.__/                                
    '''
    print(msg)

def displayMsg(msg=''):
    now = time.asctime( time.localtime(time.time()) )
    print(f'{now} - {os.getpid()}: ' + msg)

# 获取视频时长
def get_time_display(time):
    return "%02d:%02d:%02d" % (time // 3600, time % 3600 // 60, time % 60)

# 从路径中获取不包含后缀名的文件名称
def getPathName(path):
    return os.path.splitext(os.path.basename(path))[0]

# 创建略缩图
def create_thumbnail(filePath):
    fileName = getPathName(filePath)
    displayMsg('正在创建影片预览：' + fileName)
    jpg_name = fileName + '.jpg'
    if os.path.exists(jpg_name):
        displayMsg('当前影片预览已存在：' + fileName)
        return

    container = av.open(filePath)

    metadata = [
        "名称: %s" % filePath,
        "存储: %d bytes (%.2f MB)" % (container.size, container.size / 1048576),
        "时长: %s" % get_time_display(container.duration // 1000000),
    ]

    start = min(container.duration // (IMAGE_PER_ROW * IMAGE_ROWS), 5 * 1000000)
    end = container.duration - start
    time_marks = []
    for i in range(IMAGE_ROWS * IMAGE_PER_ROW):
        time_marks.append(start + (end - start) // (IMAGE_ROWS * IMAGE_PER_ROW - 1) * i)

    images = []
    for idx, mark in enumerate(time_marks):
        container.seek(mark)
        for frame in container.decode(video=0):
            images.append((frame.to_image(), mark // 1000000))
            break

    width, height = images[0][0].width, images[0][0].height

    metadata.append('参数: (%dpx, %dpx), %dkbps' % (width, height, container.bit_rate // 1024))

    metadata.append('视频资源：QQ335591758')  # 备注

    img = Image.new("RGB", (IMAGE_WIDTH, IMAGE_WIDTH), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_NAME, FONT_SIZE)
    _, min_text_height = draw.textsize("\n".join(metadata), font=font)
    image_width_per_img = int(round((IMAGE_WIDTH - PADDING) / IMAGE_PER_ROW)) - PADDING
    image_height_per_img = int(round(image_width_per_img / width * height))
    image_start_y = PADDING * 2 + min_text_height

    img = Image.new("RGB", (IMAGE_WIDTH, image_start_y + (PADDING + image_height_per_img) * IMAGE_ROWS),
                    BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)
    draw.text((PADDING, PADDING), "\n".join(metadata), TEXT_COLOR, font=font)
    for idx, snippet in enumerate(images):
        y = idx // IMAGE_PER_ROW
        x = idx % IMAGE_PER_ROW
        new_img, timestamp = snippet
        new_img = new_img.resize((image_width_per_img, image_height_per_img), resample=Image.BILINEAR)
        x = PADDING + (PADDING + image_width_per_img) * x
        y = image_start_y + (PADDING + image_height_per_img) * y
        img.paste(new_img, box=(x, y))
        draw.text((x + PADDING, y + PADDING), get_time_display(timestamp), TIMESTAMP_COLOR, font=font)

    # 图片保存
    img.save(jpg_name)
    displayMsg('影片预览创建成功：' + fileName)

# 主函数
def main():

    # 视频文件夹位置
    path = os.path.abspath(os.getcwd() + '/video')

    # 包含绝对路径的文件地址
    fileList = []
    for file in os.listdir(path):
        if os.path.splitext(file)[1] == '.mp4':
            fileList.append(os.path.join(path, file))

    os.chdir(path)
    p = Pool(10)
    displayMsg('正在将%d个影片添加到序列'% len(fileList))
    for file in fileList:
        p.apply_async(create_thumbnail, args=(file,))
    p.close()
    p.join()
    displayMsg('任务完成！')
    input('任务完成，按回车退出：')
    exit()

if __name__ == "__main__":
    welcome()
    main()
