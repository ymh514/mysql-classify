from PIL import Image

img = Image.open("/Users/Terry/Desktop/MySQLFIles/IMG_9154.JPG")
img.thumbnail((36,36))
img.save("/Users/Terry/Desktop/MySQLFIles/thumbnail.jpg")
