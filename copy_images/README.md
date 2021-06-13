### Image Organizer

- move_images.py : It can be used to move all the images to a single folder
- Image organizer.ipynb : This is used to do two things
    - First, it can be used to extract all the meta data using exiftool
    - Second, it can be used to move the images from the directory where move_images
    copied the files to an organized structure.
        - Sorted by year
        - Under each year, events are separately put in a folder. An event is a day which has >= threshold images. If consecutive days have events, then they are merged into a single event.

### Possible Improvements
- Move images in a year to subfolders by month if too many images 
  are present
- Creating a meta data database for searching / insights
- Face recognition library usage for sorting images 
- Packaging for distribution 

