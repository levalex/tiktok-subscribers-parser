import os
import argparse
import subprocess
import cv2
import pytesseract
import logging


OUTPUT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'output')


def _generate_frames(video_filename):
    subprocess.call(['ffmpeg', '-i', video_filename, '-vf', 'fps=1', os.path.join(OUTPUT_DIR, '%04d.png')])


def _get_rows(image):
    height, width, _ = image.shape

    top_offset = int(height * 0.2)
    left_offset = int(width * 0.97)
    cropped_image = image[top_offset:height, left_offset:width]


    gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.blur(gray, (10, 10))
    equalized = cv2.equalizeHist(blurred)
    _, thresh = cv2.threshold(equalized, 150, 255, cv2.THRESH_BINARY)
    s_contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    rows_y = []
    for contour in s_contours:
        (x, y, w, h) = cv2.boundingRect(contour)

        if not h > height * 0.5:
            m = cv2.moments(contour)
            rows_y.append(top_offset + int(m['m01'] / m['m00']))

    return rows_y


def _get_accounts(rows_y):
    accounts = []

    for y in rows_y:
        text_box = image[y:y + 50, 130:130 + 500]
        text = pytesseract.image_to_string(text_box)

        accounts.append(text.strip())

    return accounts


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description='Parse a file argument.')
    parser.add_argument('video_filename', type=str, help='The input file.')
    parser.add_argument('output_filename', type=str, help='The output file.')

    args = parser.parse_args()

    _generate_frames(args.video_filename)

    accounts = set()
    for filename in os.listdir(OUTPUT_DIR):
        logging.info(filename)

        image = cv2.imread(os.path.join(OUTPUT_DIR, filename))

        rows_y = _get_rows(image)
        accounts.update(_get_accounts(rows_y))

    with open(args.output_filename, 'w') as output_file:
        for account in accounts:
            output_file.write(account + '\n')
