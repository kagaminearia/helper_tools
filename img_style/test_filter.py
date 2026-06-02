import cv2
import matplotlib.pyplot as plt
import numpy as np

input_image = cv2.imread('input.jpg')

gray_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)
m, n = gray_image.shape
cv2.imwrite('gray_image.jpg', gray_image)

# thresh = 100
# ret, thresholded_image = cv2.threshold(gray_image, thresh, 255, cv2.THRESH_BINARY)
# plt.imshow(thresholded_image)
# plt.show()

# edges = cv2.Canny(gray_image, threshold1=30, threshold2=100)
threshold1 = 10
threshold2 = 100
edges = cv2.Canny(gray_image, threshold1, threshold2)

# gray multiplier
gray_multiplier = 1.5
mask = (edges == 255)
gray_image[mask] = gray_image[mask] * gray_multiplier

# cv2.imwrite("result.jpg", gray_image)



sketch_gray, sketch_color = cv2.pencilSketch(input_image, sigma_s=40, sigma_r=0.09, shade_factor=0.02)
stylize = cv2.stylization(input_image, sigma_s=60, sigma_r=0.07)

cv2.imwrite("try2.jpg", sketch_gray)
# cv2.imwrite("try2.jpg", sketch_color)



