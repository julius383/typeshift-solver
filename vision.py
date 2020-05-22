#!/usr/bin/env python

import numpy as np
import cv2
import pytesseract
from imutils.contours import sort_contours
from operator import itemgetter


def crop_to_puzzle(im, percent=0.25):
    """
    Crop image to region containing puzzle by removing a percentage
    of from the top and bottom
    """
    h, w, _ = np.shape(im)
    left, right = 0, w
    factor = int((percent * h))
    upper = 0 + factor
    lower = h - factor
    resized_image = im[upper:lower, left:right]
    return resized_image


def find_text_regions(resized_image):
    """
    Find the contours for the boxes that contain the puzzle
    letters grouping them by columns
    """
    gray = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(
        cv2.bitwise_not(gray), 180, 255, cv2.THRESH_BINARY
    )
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )
    cols = dict()
    contours = sorted(contours, key=cv2.contourArea)
    contours.pop()
    for c in contours:
        M = cv2.moments(c)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        col = cols.get(cX, [])
        col.append((c, (cX, cY)))
        cols[cX] = col
    cols = dict(sorted(cols.items()))
    return cols, gray


def extract_puzzle(cols, image):
    """
    Extract the letters of the puzzle from the contours
    """
    puzzle = []
    config = "-l eng --oem 0 --psm 10"
    for _, col in cols.items():
        r = []
        only_contours = list(map(itemgetter(0), col))
        sorted_row, sorted_rect = sort_contours(
            only_contours, method="top-to-bottom"
        )
        for row, rect in zip(sorted_row, sorted_rect):
            yv = list(filter(lambda x: np.array_equal(x[0], row), col))[0][1]
            (x, y, w, h) = rect
            x1, y1 = x + w, y + h
            roi = image[y:y1, x:x1]
            text = pytesseract.image_to_string(roi, config=config)
            r.append((text, yv))
        puzzle.append(r)
    return puzzle
