import os
import re
import subprocess
import time
import csv

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# Script Variables
FILENAME = 'internet_speedtest.csv'
HEADER = ['Date',
          'Time',
          'Ping [ms]',
          'Download Speed [Mbit/s]',
          'Upload Speed [Mbit/s]']

def main():
    try:

        # Run the Speed Test
        response = subprocess.Popen('speedtest-cli --simple',
                                    shell=True,
                                    stdout=subprocess.PIPE).stdout.read()

        # Find the Values in the String
        response_string = str(response)
        ping = re.findall('Ping:\s(.*?)\s', response_string, re.MULTILINE)
        download = re.findall('Download:\s(.*?)\s', response_string,re.MULTILINE)
        upload = re.findall('Upload:\s(.*?)\s', response_string, re.MULTILINE)

        # Convert the Values into Floats
        ping = [float(x) for x in ping]
        download = [float(x) for x in download]
        upload = [float(x) for x in upload]

    except:

        ping = [0]
        download = [0]
        upload = [0]

    # Get the Date/Time
    time_date = time.strftime('%m/%d/%y')
    time_time = time.strftime('%H:%M')

    # Create a CSV Line
    csv_line = (time_date, time_time, ping[0], download[0], upload[0])
    csv_line_string = '%s, %s, %f, %f, %f' % csv_line
    print(csv_line_string)

    # Write to CSV File
    WriteToCsv(filename=FILENAME, values=csv_line, header=HEADER)

    # Upload file to Google Drive
    drive = AuthenticateGoogleDrive()
    DeleteDriveFile(drive=drive, filename=FILENAME, folder='root')
    drive_file = drive.CreateFile()
    drive_file.SetContentFile(FILENAME)
    drive_file.Upload()


def WriteToCsv(filename, values, header=None):
    """ Take in a list of values and write them to a CSV

    If 'filename' doesn't exist, then a new file is created. If 'filename' does
    exist, it is is appended to the file.

    args:
        filename: string: Filename of the file to write to, including extension.
        values: List of values to write to the CSV
        header: List of values to write as a header to the CSV file. Will only
            write in the case that the file does not already exist
    """
    if os.path.exists(filename):

        # Append the row if the file already exists
        with open(filename, 'a') as fd:
            writer = csv.writer(fd)
            writer.writerow(values)
    else:

        # Create a new file if the file does not exist
        with open(filename, 'w') as fd:
            writer = csv.writer(fd)
            if header is not None: writer.writerow(header)
            writer.writerow(values)


def AuthenticateGoogleDrive(credentials='mycreds.txt'):
    """ Use authentication token to retun Google Drive class

    Function was first defined here:
    https://stackoverflow.com/a/24542604/5096199

    args:
        credentials: string. Name of file containing Google Drive credentials

    returns:
        drive: Instance of pydrive
    """
    gauth = GoogleAuth()

    gauth.LoadCredentialsFile(credentials)
    if gauth.credentials is None:
        # Authenticate if they're not there
        gauth.LocalWebserverAuth()

    elif gauth.access_token_expired:
        # Refresh them if expired
        gauth.Refresh()

    else:
        # Initialize the saved creds
        gauth.Authorize()
    # Save the current credentials to a file
    gauth.SaveCredentialsFile(credentials)

    drive = GoogleDrive(gauth)

    return drive


def DeleteDriveFile(drive, filename, folder='root'):
    """ Delete a file located on Google Drive

    args:
        drive: Instance of gDrive given from PyDrive
        folder: string. Name of folder where the file is located
        filename: string. Name of the file, including extension

    returns:
        drive: Instance of pydrive
    """
    list_dictionary = {'q': "'%s' in parents and trashed=false" % folder}
    file_list = drive.ListFile(list_dictionary).GetList()
    try:
        for file1 in file_list:
            if file1['title'] == filename:
                file1.Delete()
    except:
        pass


if __name__ == "__main__":
    main()
