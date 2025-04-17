"""Extract coordinates of blue and pink cell masks

Blue: mcherry / resistant
Pink: gfp / sensitive

This script extracts cell location from all images in a given directory.
Please provide the image directory in the command line when running this file.
Example: python3 mask_coords.py h358
"""

import os
import sys

import cv2
import numpy as np


def bgr_to_hsv_range(bgr):
    """Convert a color into HSV lower and upper range

    Based on:
    https://docs.opencv.org/4.11.0/df/d9d/tutorial_py_colorspaces.html

    :param bgr: The BGR values for the color
    :type bgr: tuple[int]
    :return: The lower and upper HSV range for the color
    :rtype: list[tuple[int]]
    """
    hsv_color = cv2.cvtColor(np.uint8([[bgr]]), cv2.COLOR_BGR2HSV)
    h = int(hsv_color[0][0][0])
    lower = (h - 10, 100, 100)
    upper = (h + 10, 255, 255)
    return [lower, upper]


def image_to_positions(hsv_image, color):
    """Extract centers of colored cells from HSV image

    Based on:
    https://www.geeksforgeeks.org/python-opencv-find-center-of-contour/

    :param hsv_image: The HSV image of cells
    :type hsv_image: HSV OpenCV Image
    :param color: A tuple with the cells BGR
    :type color: tuple[int]
    :return: The centers of the cells [(x1,y1),...,(xn,yn)]
    :rtype: list[tuple[int]]
    """
    # Detect cells
    mask = cv2.inRange(hsv_image, *bgr_to_hsv_range(color))

    # Segment cells
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find midpoints of cell contours
    coords = []
    for contour in contours:
        moments = cv2.moments(contour)
        moment_0 = moments["m00"]
        if moment_0 == 0:
            continue
        x = int(moments["m10"] / moment_0)
        y = int(moments["m01"] / moment_0)
        coords.append((x, y))

    return coords


def main(image_dir, debug=False):
    """For each image in the directory, save the cell coordinates as a CSV

    Cell types/colors are hardcoded at the beginning of this function

    Debug mode will display each image with the cell centers marked,
    along with the cell count information.
    Press any key while in the image window to go to the next image

    :param image_dir: The path to the image directory
    :type image_dir: str
    :param debug: whether to run in debug mode, defaults to False
    :type debug: bool, optional
    """
    cells = {"mcherry": (220, 50, 0), "gfp": (200, 0, 200)}

    for image_name in os.listdir(image_dir):
        # Check if image
        if image_name[-4:].lower() != ".png":
            continue

        # Get identifying image information
        image_name_split = image_name.split("_")
        image_id = image_name_split[2]
        well_id = image_name_split[1]
        timepoint = image_name_split[-1][:-4]

        # Read image
        bgr_image = cv2.imread(os.path.join(image_dir, image_name))

        # Convert to HSV (easier to segment by color)
        hsv_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)

        # Calculate cell positions
        positions = []
        for cell_name, cell_color in cells.items():
            coords = image_to_positions(hsv_image, cell_color)
            positions.append([cell_name, coords])

        # Write CSV
        csv_name = f"csv_{well_id}_{image_id}_{timepoint}.csv"
        with open(os.path.join(image_dir, csv_name), "w") as f:
            f.write("ImageID,Timepoint,WellID,CellType,x,y\n")
            for cell_name, coords in positions:
                for x, y in coords:
                    f.write(f"{image_id},{timepoint},{well_id},{cell_name},{x},{y}\n")

        # Show image with cell centers overlayed (debug mode)
        if debug:
            print(image_name)
            for cell_name, coords in positions:
                print(f"\t{cell_name} {len(coords)}")
                opposite_color = [255 - v for v in cells[cell_name]]
                for coord in coords:
                    cv2.circle(bgr_image, coord, 3, opposite_color, -1)
            cv2.imshow("image", bgr_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print("Please provide an image directory.")
