import os
import shutil
from datetime import datetime
import exifread
from geopy.geocoders import Nominatim
from collections import Counter
import collections
import argparse
import logging
import re
from PIL import Image

# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class ImageSorter:
    def __init__(self, input_directory, threshold, output_directory, dry_run=False):
        self.input_directory = input_directory
        self.threshold = threshold
        self.output_directory = output_directory
        self.dry_run = dry_run
        logger.debug(f"{input_directory} ==> {output_directory} [Th={threshold}")

    def get_image_files(self):
        image_files = [f for f in os.listdir(self.input_directory) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.nef'))]
        return image_files

    def get_image_date(self, image_path):
        # Attempt to read EXIF data for JPEG and PNG files
        try:
            with open(image_path, 'rb') as f:
                img = Image.open(f)
                exif_data = img._getexif()

            if exif_data and 36867 in exif_data:  # 36867 corresponds to 'DateTimeOriginal' in EXIF
                date_str = exif_data[36867]
                return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S').date()
        except (AttributeError, KeyError, IndexError, ValueError):
            pass  # Ignore if EXIF data is not present or not in the expected format

        # If EXIF data is not available, try to get the date from other metadata for RAW files
        try:
            with open(image_path, 'rb') as f:
                tags = exifread.process_file(f, stop_tag='Image DateTime')
                if 'Image DateTime' in tags:
                    date_str = str(tags['Image DateTime'])
                    return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S').date()
        except Exception:
            pass  # Ignore if other metadata is not present or not in the expected format
        # If both EXIF and other metadata reading fails, fall back to the file modification date
        return datetime.fromtimestamp(os.path.getctime(image_path)).date()


    def move_images(self):
        dry_run_limit = 40
        if self.dry_run:
          print('Dry run started')
        print(f'? discovering images in {self.input_directory}')
        image_files = self.get_image_files()
        print(f'+ discovered {len(image_files)} images')
        date_location_map = collections.defaultdict(list)

        print(f'? reading image metadata in {self.input_directory}')
        # Read date and location for all images
        date_map = dict()
        for i,image_file in enumerate(image_files):
            image_path = os.path.join(self.input_directory, image_file)
            date_taken = self.get_image_date(image_path)
            if date_taken:
                if date_taken not in date_map.keys():
                  date_map[date_taken] = [image_path]
                else:
                  date_map[date_taken].append(image_path)
            if self.dry_run and i >= dry_run_limit:
              break
        print(f'+ read image metadata in {self.input_directory}')

        logger.debug(f"Dates: {date_map.keys()}")
        # create folders
        img_count = 0
        for date, images in date_map.items():
          year_month_folder = os.path.join(f'{date.year:04d}-{date.month:02d}')
          day_folder = os.path.join(f'{date.year:04d}-{date.month:02d}-{date.day:02d}')
          # check if multiple images were taken that day
          if len(images) > self.threshold:
            # see if there is a common address
            common_address = self.get_common_address(images)
            print('common address:', common_address)
            if common_address is not None:
              day_folder += common_address
            move_to = day_folder

          else:
            move_to = year_month_folder

          move_to = os.path.join(self.output_directory, move_to)
          if not os.path.exists(move_to) and not self.dry_run:
                os.makedirs(move_to)
          for image_file in images:
              image_path = os.path.join(self.input_directory, image_file)

              if not self.dry_run:
                  shutil.move(image_path, move_to)
              img_count +=1
              print(f'{image_file} [taken on:{date}] moved to {move_to}')

          if self.dry_run and img_count > 50:
            return

    def convert_gps_to_decimal(self, gps_data, direction):
      print(gps_data, direction)
      degrees_num, minutes_num, seconds_frac = gps_data.values
      dd = float(degrees_num) + float(minutes_num)/60 + float(seconds_frac)/(60*60);
      if direction == 'S' or direction == 'W':
          dd *= -1
      return dd

    def trim_location(self, location):
      if location is None:
        return location
      print(location, end=' ==>')
      location = re.sub(r'\W+', '_', location)
      if len(location) > 32:
        location = location[:16] + '__' +location[-14:]
      print(location)
      return location

    def extract_location(self, image_path):
        with open(image_path, 'rb') as f:
            tags = exifread.process_file(f, stop_tag='GPS GPSLatitude')
            if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
                latitude = self.convert_gps_to_decimal(tags['GPS GPSLatitude'], tags['GPS GPSLatitudeRef'])
                longitude = self.convert_gps_to_decimal(tags['GPS GPSLongitude'],tags['GPS GPSLongitudeRef'] )
                location = self.reverse_geocode(latitude, longitude)
                print(image_path, latitude, longitude, location)
                return location
            else:
                return None

    def extract_city_country_from_address(self, address):
      import pdb;pdb.set_trace()

      geolocator = Nominatim(user_agent="address-extractor")
      try:
          location_info = geolocator.geocode(address, language='en', addressdetails=True)
          if location_info and location_info.address:
              city = location_info.address.get('city', '')
              country = location_info.address.get('country', '')
              return city, country
      except Exception as e:
          print(f'Error in geocoding: {e}')

      return None, None

    def reverse_geocode(self, latitude, longitude):
        geolocator = Nominatim(user_agent="image-sorter")
        try:
            location_info = geolocator.reverse((latitude, longitude), language='en', addressdetails=True, timeout=10)
            if location_info and location_info.address:
              # import pdb;pdb.set_trace()
              loc_raw = location_info.raw
              if 'neighbourhood' in loc_raw['address'].keys():
                ne = loc_raw['address']['neighbourhood'] + '_'
              else:
                ne = ''
              city = loc_raw['address']['city']
              country = loc_raw['address']['country_code']
              return f'{ne}{city}_{country}'
            return location_info.address if location_info else None
        except :
          print("error")
          return None


    def get_common_address(self, images):
        addresses = []
        for image in images:
          curr_addr = self.extract_location(image)
          if curr_addr is not None:
            addresses.append(self.trim_location(curr_addr))
        try:
          # Find the most common address
          common_address, count = Counter(addresses).most_common(1)[0]
          print(addresses, common_address, count)

          return common_address
        except Exception as e:
          return None



def main():
    parser = argparse.ArgumentParser(description='Sort and organize images based on date and location.')
    parser.add_argument('input_directory', help='Path to the input directory containing images.')
    parser.add_argument('threshold', type=int, help='Threshold for image count on a specific day.')
    parser.add_argument('output_directory', help='Path to the output directory for organized images.')
    parser.add_argument('--dry-run', action='store_true', help='Perform a dry run, showing which files will be moved without actually copying.')

    args = parser.parse_args()

    image_sorter = ImageSorter(args.input_directory, args.threshold, args.output_directory, args.dry_run)
    image_sorter.move_images()

    # Example usage:
    # gps_locations = [(latitude1, longitude1), (latitude2, longitude2), ...]
    # image_sorter.get_common_address(gps_locations)


if __name__ == '__main__':
    main()
