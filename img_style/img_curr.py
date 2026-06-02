import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

def edge_mask(img, line_size, blur_value):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_blur = cv2.medianBlur(gray, blur_value)
    edges = cv2.adaptiveThreshold(gray_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, line_size, blur_value)
    return edges

def gray_quantization(img, num_levels):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    step_size = 255 / (num_levels - 1)
    quantized_img = np.round(gray_img / step_size) * step_size
    return quantized_img

# not used 
def extract_regions(quantized_img, target_level):
    mask = (quantized_img == target_level)
    region_pixels = np.where(mask)
    return region_pixels



def analyze_img(input):
    # img = cv2.imread("input2.jpg")
    img = cv2.cvtColor(input, cv2.COLOR_BGR2RGB)

    # Convert to grayscale
    grayimg = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    line_size = 9
    blur_value = 3
    edges = edge_mask(img, line_size, blur_value)
    # plt.imshow(edges)
    # plt.show()

    num_levels = 5
    quantized_image = gray_quantization(img, num_levels)
    # plt.imshow(quantized_image)
    # plt.show()

    sketch_gray, sketch_color = cv2.pencilSketch(img, sigma_s=40, sigma_r=0.09, shade_factor=0.02)
    quantized_image_float = quantized_image.astype(np.float32)
    sketch_gray_float = (sketch_gray * 255).astype(np.float32)

    # ans = cv2.bitwise_and(quantized_image, quantized_image, mask=sketch_gray)

    alpha = 0.4
    blended = cv2.addWeighted(quantized_image_float, 1 - alpha, sketch_gray_float, alpha, 0)
    blended = np.clip(blended, 0, 255).astype(np.uint8)

    return blended
    # plt.imshow(ans)
    # plt.show()
    # cv2.imwrite("ans2.jpg", blended)




input_folder = "input"
output_folder = "output"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)


# Get a list of image file names in the input folder
image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
print('complete getting list of image')

for image_file in image_files:
    input_path = os.path.join(input_folder, image_file)
    output_path = os.path.join(output_folder, image_file)

    # Load the image using cv2
    img = cv2.imread(input_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Call the analyze_img function
    output = analyze_img(img)

    # Save the processed image
    cv2.imwrite(output_path, output)
    print('complete one image')

print("Processing and saving complete.")


