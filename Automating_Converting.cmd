#rs.convert.exe all must exist within this directory, make a copy
#chnage the directory to where the .bag files are

cd /d E:\Bag_files\2-22-23

#Creates a directory with the same name as the .bag file
for /r %I in (*.bag) do mkdir %~pI%~nI

#Converts the bag files into png files
for /r %I in (*.bag) do rs-convert.exe -d -i %I -p %~pI%~nI\

#Converst the bag files into csv files
for /r %I in (*.bag) do rs-convert.exe -d -i %I -v %~pI%~nI\
