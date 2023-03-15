% Install the image package
pkg load image

% Read the pig image
Depth = imread("~/Downloads/_Depth_2021.png");
Depth = imread("~/Downloads/_Depth_18510.png");

% Display the image
imshow(Depth)

% Cow pixel values
impixel(Depth, 500, 260) 
% Ground pixel values
impixel(Depth, 610, 55)

% Convert the Depth image to gray image
I = rgb2gray(Depth);
imshow(I)

% Use im2bw because imbinarize is not implemented yet in Octave
% Convert image to binary image
BW1 = im2bw(I);
imshow(BW1); 

% Alternative approach
% Convert RGB colors to HSV (Hue, Saturation, and Value)
hsvImage = rgb2hsv(Depth);
% Display the HSV image
imshow(hsvImage)
% Convert image to binary image
BW2 = im2bw(hsvImage);
imshow(BW2); 

% Hue
hImage = hsvImage(:, :, 1);
% Saturation
sImage = hsvImage(:, :, 2);
% Value
vImage = hsvImage(:, :, 3);
% Display Hue, Saturation, and Value
montage(cat(1, hImage, sImage, vImage));

% We will use the hue image for segmentation 
imshow(hImage)
% Convert image to binary image
BW3 = im2bw(hImage, 0.2);
imshow(BW3)


% Remove stuructures connected to the image border
BW4 = imclearborder(BW3);
imshow(BW4);
montage(cat(1, BW3, BW4));

% Extract the largest object from binary image
BW5 = bwpropfilt(BW4,'Area',1);
imshow(BW5);
montage(cat(1, BW4, BW5));

% close holes
se = strel('diamond', 5);
BW6 = imclose(BW5, se);
montage(cat(1, BW5, BW6));


% Extract image features
box6 = regionprops(BW6, 'FilledArea', 'Area', 'BoundingBox','MajorAxisLength','MinorAxisLength', 'Centroid', 'Orientation', 
'Extent', 'Eccentricity')
% Draw a bounding box
imshow(BW6);
rectangle('Position', box6.BoundingBox, 'EdgeColor','r', 'LineWidth',5)
