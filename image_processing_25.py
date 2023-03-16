#Image processing libraries
from ctypes.wintypes import RGB
import numpy as np
import pandas as pd
from audioop import avg
import cv2
from PIL import Image

#Statistics Library
from audioop import avg
from scipy.spatial import distance as dist
import matplotlib.pyplot as plt
from scipy import stats
import statistics
import xlsxwriter
import math

#Moving through directoriess
import os
from importlib.resources import path

#This is the directory where the images are. The directory contains subfolders. 1 subfolder for each cow.
#The subfolder contain images and CSV files for the cow.
directory = r"C:\Users\katie\Desktop\Senior_Design\directory"

#Iterate through the directoires in the main directory
for root, dirs, files in os.walk(directory): #Checks everthing listed in directory

    #find any of the subfolders within
    for dir in dirs: #find all the subdirectories within larger parent directory
        subdir = os.path.join(directory, dir)
        images = [x for x in os.listdir(subdir) if ".png"]
        csvs = [x for x in os.listdir(subdir) if ".xlsx"]

        #Initialize the data lists
        length_list = []
        width_list = []
        depth_list = []
        volume_list = []   
        img_list = []
        csv_list = []

        for img in images:
            img_name = str(img.removesuffix(".png"))
            img_list.append(img_name)
        for csv in csvs:
            csv_name = str(csv.removesuffix(".csv"))
            # add the csv file to the csv list
            csv_list.append(csv_name)

        #Set up a excel file and sheet
        workbook = xlsxwriter.Workbook(str(os.path.basename(subdir))+'.xlsx')
        worksheet = workbook.add_worksheet()
        worksheet.write('A1', 'Length')
        worksheet.write('B1', 'Width')
        worksheet.write('C1', 'Height')

        #check to see if the img name and csv file name are the same
        for img_name in img_list:
            for csv_name in csv_list:
                if img_name == csv_name:

                    #reconstruct csv and img paths     
                    csv_img = pd.read_csv(subdir + '\\' + csv_name + '.csv', header = None, engine ='python')
                    img = cv2.imread(subdir + '\\' + img_name + '.png' )[0:480,0:848]

                    #COnvert to hue, saturation, and value, and split the images
                    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                    h,s,v = cv2.split(hsv_img)
                    hsv_split = np.concatenate((h,s,v),axis=1)

                    # Use the hue image to convert to binary
                    thresh = 20 #thresh hold for converting into black or white
                    thresh, thresh_img = cv2.threshold(h, thresh, 255, cv2.THRESH_BINARY)
            
                    # Erode the image to seperate the head and neck
                    kernel = np.ones((49,49), np.uint8) #determines the size of the matrix to extract the images
                    img_erosion = cv2.erode(thresh_img, kernel, iterations=1)

                    #Finds all the contours in the image
                    # Use a copy of the image since findContours alters the image
                    contours, hierarchy = cv2.findContours(img_erosion.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                    
                    #Extract the largest contour area
                    c = max(contours, key=cv2.contourArea)

                    #draws the largest contour back onto the image
                    mask = np.zeros(img_erosion.shape, dtype=img_erosion.dtype)
                    drawing = cv2.drawContours(mask, [c], 0, (255), -1)

                    #re-dilate the image after finding the largest area to get just the body
                    img_dilation = cv2.dilate(drawing, kernel, iterations=1)

                    # Find the contours of the redilated images (the redilated image is just the body)
                    contours2 = cv2.findContours(img_dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    contours2 = contours2[0] if len(contours2) == 2 else contours2[1]

                    #Draw the bonding rectangle around the body
                    for i in contours2:
                        x,y,Length,Width = cv2.boundingRect(i)
                        cv2.rectangle(img_dilation, (x, y), (x + Length, y + Width), (255,0,0), 4)

                    #adds the length and width from the images to the length and width list
                    length_list.append(Length)
                    width_list.append(Width)

                    #Get the coordinates of the segmented image and print the pixels
                    stats.describe(np.ravel(drawing)) #returns a 1 Dimentional array
                    pixel = np.argwhere(drawing == 255) #finds where the image is white (cow)
                    pixel[0:4,]

                    csv_img_rows = []
                    for row, col in pixel[0:480,0:848]:
                        csv_img_rows.append([row, col, csv_img.iloc[row,col]])#finds the row and column values of the cow

                    #Convert the variable to a pandas data frame - easier to remove outliers
                    df = pd.DataFrame(csv_img_rows, columns = ['row', 'col', 'dist'])
                    df.describe()
                    ds0 = np.array(df.dist) 

                    #Remove the outliers
                    df.dist.replace(to_replace=0, value = df.dist.mean(), inplace=True)
                    df.describe()

                    #Use the median to find the average
                    distMean = df.dist.median()
                    height = 2.5 - distMean

                    #Add value to the depth list
                    depth_list.append(height)

                    #calculating volume by finding the sum of all the heights in the white (cow) area
                    df["height"] = 2.5 - df["dist"]
                    volume = sum(df.height)
                    volume_list.append(volume)
                else:
                    False
        #Initialize the rows in excel file
        d_row = 1
        w_row = 1
        l_row = 1
        v_row = 1

        #Interate through each list, and add the number to the excel sheet
        for item in depth_list:
            worksheet.write_number(d_row,2,item)
            d_row += 1
        for item in width_list:
            worksheet.write_number(w_row,1,item)
            w_row += 1
        for item in length_list:
            worksheet.write_number(l_row,0,item)
            l_row += 1
        for item in volume_list:
            worksheet.write_number(v_row,3,item)
            v_row += 1

        #calcualates the ellipsoid volume
        #0.00530649 m = 1 pixel
        ellipoid_vol = (((1/3)*(statistics.median(depth_list)))*((1/2)*(statistics.median(width_list))*0.00530649)*
                        ((1/2)*(statistics.median(length_list))*0.00530649)*(4/3)*(math.pi))
                        
        #Find the median of these values and put them in the excel file
        #Create headers for the columns in excel
        worksheet.write('F1','Median Width in Pixels')
        worksheet.write('G1','Median Length in Pixels')
        worksheet.write('F3','Median Width in Meters')
        worksheet.write('G3','Median Length in Meters')
        worksheet.write('H1','Mean Depth')
        worksheet.write('I1', 'Median Depth')
        worksheet.write('J1', 'Average Volume')
        worksheet.write('K1', 'Ellipsoid Method Volume')

        #writes the mean, median, and volume values into the excel sheet
        worksheet.write_number('F2', statistics.median(width_list))
        worksheet.write_number('G2', statistics.median(length_list))
        worksheet.write_number('F4', 0.00530649 * statistics.median(width_list))
        worksheet.write_number('G4', 0.00530649 * statistics.median(length_list))
        worksheet.write_number('H2', statistics.mean(depth_list))
        worksheet.write_number('I2', statistics.median(depth_list))
        worksheet.write_number('J2', statistics.median(volume_list))
        worksheet.write_number('K2', ellipoid_vol)

        #close the worksheet
        workbook.close()
