#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

    Automatic FFMPEG Transcoding Handler Script
    Copyright © 2021 by WebMaka
    
    
    FOR MORE INFORMATION
    
    What this does, how to use it, and more can be found on its GitHub
    repo at this URL:
    
    https://github.com/WebMaka/AutoTranscode
    
    
    
    PLEASE SUPPORT MY PROJECTS
    
    If this script helps your workflow, please consider donating to help 
    support my projects, including this one. Any amount helps and will be
    very much appreciated.
    
    As a thank-you for supporting my work, donators and Patrons get early access
    to updates to this script, as well as having a means to directly request
    features.
    
    To donate via PayPal, please follow this link:
    
    https://www.paypal.com/donate?hosted_button_id=GMFCGQALGUNYG
    
    To donate via Patreon, please follow this link:
    
    https://www.patreon.com/webmaka
    
    
    
    IMPORTANT NOTE
    
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at the author's option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see the following:
    
    https://www.gnu.org/licenses/gpl-3.0.html

"""


# Imports
import configparser
import datetime
import os
import re
import shutil
import subprocess
import sys
import time
import traceback


#
# Default Variables/Settings
#
# NOTE: These are the base settings that get overridden by command-line arguments.
#

# Debug mode - writes script's activities (but not ffmpeg output) to log files.
# CAUTION: logs can get big.
debug_mode = False

# Write ffmpeg output to log files.
# CAUTION: logs can get big.
save_ffmpeg_output = False

# Full path to ffmpeg (unless it's in the system's PATH - if it cannot be reached
# via just "ffmpeg," the full path will be needed here.
ffmpeg_location = 'ffmpeg'

# Target directory to monitor
source_dir = ''

# File extensions to flag
file_exts = ["avi", "m4v", "mkv", "mov", "mp4", "webm", "wmv"]

# Target directory for transcodes
dest_dir = ''

# Target directory to move files once transcodes are completed
# NOTE: If this var is empty, files will be renamed and given a ".processed"
# extension once the transcode finishes. This way they won't be reprocessed.
storage_dir = ''

# File countdown time - if a file has stopped changing sizes, wait (this value
# * loop delay time) seconds before processing it.
countdown_time = 2

# Transcoded file extension, e.g., "mov" for Quicktime MOV, "mp4" for MPEG4,
# "mkv" for Matroska, etc.
new_ext = ''

# FFMPEG argument list storage
cmdline = []

# Transcode description, filled in when a transcode mode is selected.
trans_mode = ''


# Get our script's directory.
path = os.path.dirname(os.path.realpath(__file__))
if not path.endswith(os.path.sep):
    path += os.path.sep


# Show some Copyright/version/legal messages.
script_name = "Automatic FFMPEG Transcoding Handler Script"
version = "0.3"
print(" ")
print("{} ({})" . format(script_name, sys.argv[0]))
print("Version {}" . format(version))
#
# NOTE: It is a violation of the script's license to edit the following
# Copyright notice. And it's also mean-spirited. So please don't.
#
print("Copyright (C) 2021 by WebMaka.")
print("See documentation for usage details and license.")
#
# END NOTE
#
print(" ")

# Parse command-line arguments.
if len(sys.argv) > 1:
    index = 1
    while index < len(sys.argv):

        # Fetch the next argument to process.
        argument = sys.argv[index]


        # Davinci Resolve (Linux) import transcode
        if argument.lower() == "-davinci":
            # These settings build import files for Davinci Resolve 16.2 on Linux,
            # and will transcode things like Twitch streams into a format that
            # Resolve will work with without requiring further alteration.
            cmdline = [
                          #"%FFMPEG%", # Required for obvious reasons and must be #1
                          "-y", # Assume "yes" to prompts, e.g., overwrite warning
                          "-progress -", # Output progress info (and yes that hyphen is REQUIRED)
                          "-nostats", # Don't output a bunch of statistical info on the file
                          "-hwaccel auto", # Hardware acceleration enabled, auto-detect
                          "-i %SOURCEFILE%", # Name of file to transcode
                          "-c:v mpeg4", # Transcode video to MPEG4
                          "-qscale:v 1", # Set video quality to max
                          "-c:a pcm_s16le", # Transcode audio to 16-bit PCM (LE byte order)
                          "-b:v 36m", # Set bitrate to 36mbps
                          "-r 60", # Force framerate of output to 60FPS (add/drop frames)
                          "-f %NEWEXT%", # Transcode into container based on "new_ext" variable
                          "%DESTFILE%" # Name and path for trandcode output (should be last)
                       ]

            # Set the extension to MOV.
            new_ext = "mov"

            # Set the description for later display.
            trans_mode = "Davinci Resolve 16+ Import - MPEG4 video, 16-bit PCM audio, MOV container"


        # Youtube upload H.264 transcode
        elif argument.lower() == "-youtube":
            # These settings are for transcoding edited videos into a format
            # that uploads quickly to Youtube. It follows the recommended
            # encoding spec guidelines for Youtube as of 15 Dec 2020.
            cmdline = [
                          #"%FFMPEG%", # Required for obvious reasons and must be #1
                          "-y", # Assume "yes" to prompts, e.g., overwrite warning
                          "-progress -", # Output progress info (and yes that second hyphen is REQUIRED)
                          "-nostats", # Don't output a bunch of statistical info on the file
                          "-hwaccel auto", # Hardware acceleration enabled, auto-detect
                          "-i %SOURCEFILE%", # Name of file to transcode
                          #"-s 1920x1080", # Set output size to 1920x1080
                          "-pix_fmt yuv420p", # Set pixel format to 4:2:0 YUV
                          "-c:v libx264", # Transcode video to H.264
                          "-b:v 75m", # Set video bitrate to 75mbps, which is for 4K HDR - the rate will be much smaller for lower resolution videos
                          "-profile:v high", # High profile
                          "-bf 2", # Set B-frame generation to two consecutive
                          "-c:a aac", # Transcode audio to AAC
                          "-g 30", # Force GOP to 1/2 framerate
                          "-crf 18", # Set CRF to something middle-of-the-road
                          "-use_editlist 0", # No edit lists
                          "-movflags +faststart", # Relocate MOOV atom to beginning of file
                          "-r 60", # Force framerate of output to 60FPS (add/drop frames)
                          "-f %NEWEXT%", # Transcode into container based on "new_ext" variable
                          "%DESTFILE%" # Name and path for trandcode output (should be last)
                      ]

            # Set the extension to MP4.
            new_ext = "mp4"

            # Set the description for later display.
            trans_mode = "Youtube upload - H.264 video, AAC audio, MP4 container"


        # Avid DNxHR-HQ transcode
        elif argument.lower() == "-dnxhr":
            # These settings are for transcoding edited videos into a popular
            # working format for professional video editing. The files can be
            # huge, but the resulting quality is about as good as it gets.
            cmdline = [
                          #"%FFMPEG%", # Required for obvious reasons and must be #1
                          "-y", # Assume "yes" to prompts, e.g., overwrite warning
                          "-progress -", # Output progress info (and yes that second hyphen is REQUIRED)
                          "-nostats", # Don't output a bunch of statistical info on the file
                          "-hwaccel auto", # Hardware acceleration enabled, auto-detect
                          "-i %SOURCEFILE%", # Name of file to transcode
                          "-c:v dnxhd", # Transcode video to DNxHD
                          "-profile:v dnxhr_hq", # HQ profile
                          "-c:a pcm_s16le", # Transcode audio to 16-bit PCM (LE byte order)
                          "-pix_fmt yuv422p", # Set pixel format to 4:2:2 YUV
                          "-f %NEWEXT%", # Transcode into container based on "new_ext" variable
                          "%DESTFILE%" # Name and path for trandcode output (should be last)
                      ]

            # Set the extension to MOV.
            new_ext = "mov"

            # Set the description for later display.
            trans_mode = "DNxHR HQ video, 16-bit PCM audio, MOV container"


        # Apple ProRes 4444 transcode
        elif argument.lower() == "-prores":
            # These settings are for transcoding edited videos into a popular
            # working format for professional video editing. The files can be
            # huge, but the resulting quality is about as good as it gets.
            cmdline = [
                          #"%FFMPEG%", # Required for obvious reasons and must be #1
                          "-y", # Assume "yes" to prompts, e.g., overwrite warning
                          "-progress -", # Output progress info (and yes that second hyphen is REQUIRED)
                          "-nostats", # Don't output a bunch of statistical info on the file
                          "-hwaccel auto", # Hardware acceleration enabled, auto-detect
                          "-i %SOURCEFILE%", # Name of file to transcode
                          "-pix_fmt yuv422p10le", # Set pixel format to 4:2:2 YUV, 10 bits per pixel
                          "-c:v prores_ks", # Set codec to ProRes
                          "-profile:v 4", # 4444 profile
                          "-c:a pcm_s24le", # Transcode audio to 24-bit PCM (LE byte order)
                          "-f %NEWEXT%", # Transcode into container based on "new_ext" variable
                          "%DESTFILE%" # Name and path for trandcode output (should be last)
                      ]

            # Set the extension to MOV.
            new_ext = "mov"

            # Set the description for later display.
            trans_mode = "ProRes 4444 video, 24-bit PCM audio, MOV container"


        # Plex "nearly universal" HD (1080p) H.264 transcode
        elif argument.lower() == "-plexhd":
            # These settings are for transcoding edited videos into a format
            # that plays without additional transcoding on a wide variet of Plex
            # clients. This minimizes the demand on the server for client
            # transcodes. NOTE: Non-HD video is scaled, and non-16:9 aspect
            # ratio video is either letterboxed or pillarboxed as required.
            cmdline = [
                          #"%FFMPEG%", # Required for obvious reasons and must be #1
                          "-y", # Assume "yes" to prompts, e.g., overwrite warning
                          "-progress -", # Output progress info (and yes that second hyphen is REQUIRED)
                          "-nostats", # Don't output a bunch of statistical info on the file
                          "-hwaccel auto", # Hardware acceleration enabled, auto-detect
                          "-i %SOURCEFILE%", # Name of file to transcode
                          "-vf scale=\"'if(gt(a,16/9),1920,-1)':'if(gt(a,16/9),-1,1080)', pad=1920:1080:(1920-iw*min(1920/iw\,1080/ih))/2:(1080-ih*min(1920/iw\,1080/ih))/2\"", # Scale to 1920 wide and/or 1080 high regardless of aspect ratio, and pad extra space for non-16:9 ratios (letterbox or pillarbox)
                          "-af \"aresample=async=1:min_hard_comp=0.100000:first_pts=0\"", # Audio resample to prevent desync
                          "-pix_fmt yuv420p", # Set pixel format to 4:2:0 YUV
                          "-c:v libx264", # Transcode video to H.264
                          "-level:v 4.0", # Set H.264 level to 4.0, which supports 1080p30 @ up to 20mbps
                          "-profile:v high", # High profile
                          "-b:v 8m", # Set video bitrate to 8mbps
                          "-c:a aac", # Transcode audio to AAC
                          "-b:a 320k", # Set audio bitrate to 320kbps
                          "-movflags +faststart", # Relocate MOOV atom to beginning of file
                          "-r 30", # Force framerate of output to 30FPS (add/drop frames)
                          "-crf 18", # Set CRF to something middle-of-the-road
                          "-f %NEWEXT%", # Transcode into container based on "new_ext" variable
                          "%DESTFILE%" # Name and path for trandcode output (should be last)
                      ]

            # Set the extension to MP4.
            new_ext = "mp4"

            # Set the description for later display.
            trans_mode = "Plex HD - H.264 video, AAC audio, MP4 container"


        # Plex "nearly universal" SD (720p) H.264 transcode
        elif argument.lower() == "-plexsd":
            # These settings are for transcoding edited videos into a format
            # that plays without additional transcoding on a wide variet of Plex
            # clients. This minimizes the demand on the server for client
            # transcodes. NOTE: Non-SD video is scaled, and non-16:9 aspect
            # ratio video is either letterboxed or pillarboxed as required.
            cmdline = [
                          #"%FFMPEG%", # Required for obvious reasons and must be #1
                          "-y", # Assume "yes" to prompts, e.g., overwrite warning
                          "-progress -", # Output progress info (and yes that second hyphen is REQUIRED)
                          "-nostats", # Don't output a bunch of statistical info on the file
                          "-hwaccel auto", # Hardware acceleration enabled, auto-detect
                          "-i %SOURCEFILE%", # Name of file to transcode
                          "-vf scale=\"'if(gt(a,16/9),1280,-1)':'if(gt(a,16/9),-1,720)', pad=1280:720:(1280-iw*min(1280/iw\,720/ih))/2:(720-ih*min(1280/iw\,720/ih))/2\"", # Scale to 1280 wide and/or 720 high regardless of aspect ratio, and pad extra space for non-16:9 ratios (letterbox or pillarbox)
                          "-af \"aresample=async=1:min_hard_comp=0.100000:first_pts=0\"", # Audio resample to prevent desync
                          "-pix_fmt yuv420p", # Set pixel format to 4:2:0 YUV
                          "-c:v libx264", # Transcode video to H.264
                          "-level:v 4.0", # Set H.264 level to 4.0, which supports 1080p30 @ up to 20mbps
                          "-profile:v baseline", # Baseline profile
                          "-b:v 4m", # Set video bitrate to 4mbps
                          "-c:a aac", # Transcode audio to AAC
                          "-b:a 320k", # Set audio bitrate to 320kbps
                          "-movflags +faststart", # Relocate MOOV atom to beginning of file
                          "-r 30", # Force framerate of source to 30FPS (add/drop frames)
                          "-crf 18", # Set CRF to something middle-of-the-road
                          "-f %NEWEXT%", # Transcode into container based on "new_ext" variable
                          "%DESTFILE%" # Name and path for trandcode output (should be last)
                      ]

            # Set the extension to MP4.
            new_ext = "mp4"

            # Set the description for later display.
            trans_mode = "Plex SD - H.264 video, AAC audio, MP4 container"


        # WebM (VP9) Constant-Quality single-pass transcode
        elif argument.lower() == "-webm":
            cmdline = [
                          #"%FFMPEG%", # Required for obvious reasons and must be #1
                          "-y", # Assume "yes" to prompts, e.g., overwrite warning
                          "-progress -", # Output progress info (and yes that second hyphen is REQUIRED)
                          "-nostats", # Don't output a bunch of statistical info on the file
                          "-hwaccel auto", # Hardware acceleration enabled, auto-detect
                          "-i %SOURCEFILE%", # Name of file to transcode
                          "-c:v libvpx-vp9", # Transcode to VP9
                          "-crf 30", # Set CRF to something middle-of-the-road
                          "-b:v 0", # Force CONSTANT-QUALITY mde
                          "-f %NEWEXT%", # Transcode into container based on "new_ext" variable
                          "%DESTFILE%" # Name and path for trandcode output (should be last)
                      ]

            # Set the extension to MOV.
            new_ext = "webm"

            # Set the description for later display.
            trans_mode = "WebM (VP9) Constant-Quality Single-Pass"


#        # Add your own transcode arguments!
#        elif argument.lower() == "-newtranscode":
#            # Edit the following to add the components of a command line call
#            # for ffmpeg. As is the case for calling ffmpeg directly, order
#            # does matter. Enable ffmpeg logging by setting the "save_ffmpeg_output"
#            # variable to True if your transcode fails - that way, you can inspect
#            # ffmpeg's output to see what's making it upset.
#
#            # Please note the following tokens are allowed:
#            #   %FFMPEG% : Full path to ffmpeg (defaults to "ffmpeg" but requires ffmpeg to
#            #              be in a directory on the system's PATH)
#            #   %SPATH% : Source directory provided by caller (not generally needed here)
#            #   %DPATH% : Destination directory provided by caller (not generally needed here)
#            #   %SOURCEFILE% : target file (filename, with full path)
#            #   %DESTFILE% : destination file (filename, with full path, but with NEW extension)
#            #   %NEWEXT% : New file extension, taken from the "new_ext" variable
#            cmdline = [
#                          #"%FFMPEG%", # Required for obvious reasons and must be #1
#                          "-y", # Assume "yes" to prompts, e.g., overwrite warning
#                          "-progress -", # Output progress info (and yes that second hyphen is REQUIRED)
#                          "-nostats", # Don't output a bunch of statistical info on the file
#                          "-hwaccel auto", # Hardware acceleration enabled, auto-detect
#                          #
#                          # Add your specific INPUT flags and settings here. See the other
#                          # transcode entries for examples.
#                          #
#                          "-i %SOURCEFILE%", # Name of file to transcode
#                          #
#                          # Add your specific OUTPUT flags and settings here. See the other
#                          # transcode entries for examples.
#                          #
#                          "-f %NEWEXT%", # Transcode into container based on "new_ext" variable
#                          "%DESTFILE%" # Name and path for trandcode output (should be last)
#                      ]
#
#            # Set the extension to MOV.
#            new_ext = "mov"
#
#            # Set the description for later display.
#            trans_mode = "Briefly describe the transcode's results here."


        # Source directory
        elif argument.lower() == "-s":

            # Sanity check - is there a trailing argument?
            if index + 1 >= len(sys.argv):
                print("Missing argument - please check your command line.")
                quit()

            # Fetch the next argument, which SHOULD be the source directory.
            temp = sys.argv[index + 1].strip('"')

            # Sanity check - is the next argument an actual path?
            if not os.path.isdir(temp):
                print("Source directory doesn't exist - please check your command line.")
                quit()

            # We've passed the sanity checks, so let's store this argument.
            source_dir = temp

            # Advance the index an extra step, skipping the next since it's a
            # parameter.
            index += 1


        # Destination directory
        elif argument.lower() == "-d":

            # Sanity check - is there a trailing argument?
            if index + 1 >= len(sys.argv):
                print("Missing argument - please check your command line.")
                quit()

            # Fetch the next argument, which SHOULD be the destination directory.
            temp = sys.argv[index + 1].strip('"')

            # Sanity check - is the next argument an actual path?
            if not os.path.isdir(temp):
                print("Destination directory doesn't exist - please check your command line.")
                quit()

            # We've passed the sanity checks, so let's store this argument.
            dest_dir = temp

            # Advance the index an extra step, skipping the next since it's a
            # parameter.
            index += 1


        # Finished-transcode storage directory
        elif argument.lower() == "-f":

            # Sanity check - is there a trailing argument?
            if index + 1 >= len(sys.argv):
                print("Missing argument - please check your command line.")
                quit()

            # Fetch the next argument, which SHOULD be the storage directory.
            temp = sys.argv[index + 1].strip('"')

            # Sanity check - is the next argument an actual path?
            if not os.path.isdir(temp):
                print("Transcode storage directory doesn't exist - please check your command line.")
                quit()

            # We've passed the sanity checks, so let's store this argument.
            storage_dir = temp

            # Advance the index an extra step, skipping the next since it's a
            # parameter.
            index += 1


        # ffmpeg location
        elif argument.lower() == "-ffmpeg":

            # Sanity check - is there a trailing argument?
            if index + 1 >= len(sys.argv):
                print("Missing argument - please check your command line.")
                quit()

            # Fetch the next argument, which SHOULD be the source directory.
            temp = sys.argv[index + 1].strip('"')

            # Sanity check - is the next argument an actual path?
            if not os.path.isdir(temp):
                print("ffmpeg directory doesn't exist - please check your command line.")
                quit()

            # Sanity check - can we find ffmpeg via this path?
            if not os.path.isfile(os.path.join(temp, "ffmpeg.exe")):
                print("ffmpeg doesn't exist in the provided location - please check your command line.")
                quit()

            # We've passed the sanity checks, so let's store this argument.
            ffmpeg_location = os.path.join(temp, "ffmpeg.exe")

            # Advance the index an extra step, skipping the next since it's a
            # parameter.
            index += 1


        # Config file location
        elif argument.lower() == "-conf":

            # Sanity check - is there a trailing argument?
            if index + 1 >= len(sys.argv):
                print("Missing argument - please check your command line.")
                quit()

            # Fetch the next argument, which SHOULD be the source directory.
            temp = sys.argv[index + 1].strip('"')

            if not os.path.isfile(temp):
                print("Config file doesn't exist in the provided location - please check your command line.")
                quit()

            # Parse the config file.
            config = configparser.ConfigParser(allow_no_value=True)

            # We've passed the sanity checks, so let's grab the config file's
            # contents into a config file parser.
            with open(temp, 'r') as config_file: 
                config.read_file(config_file)

            # Parse values into variables. Note that we will only change
            # a variable if the config file contains an entry for that
            # variable, which means that the config file overrides the
            # script's commandline BUT the commandline can provide data that
            # is missing from the config file.
            if config.has_option("paths", "source"):
                temp = config.get("paths", "source", raw=True)
                if temp != "":
                    source_dir = temp
            if config.has_option("paths", "destination"):
                temp = config.get("paths", "destination", raw=True)
                if temp != "":
                    dest_dir = temp
            if config.has_option("paths", "finished"):
                temp = config.get("paths", "finished", raw=True)
                if temp != "":
                    storage_dir = temp
            if config.has_option("paths", "ffmpeg"):
                temp = config.get("paths", "ffmpeg", raw=True)
                if temp != "":
                    ffmpeg_location = os.path.join(temp, "ffmpeg.exe")
            if config.has_option("monitor", "extensions"):
                temp = config.get("monitor", "extensions").split(',')
                if temp != "":
                    file_ext = temp
            if config.has_option("transcode", "custom"):
                temp = config.get("transcode", "custom", raw=True)
                if temp != "":
                    cmdline.append(temp)
                    trans_mode = "Custom-defined ffmpeg commandline"
            if config.has_option("transcode", "container"):
                temp = config.get("transcode", "container")
                if temp != "":
                    new_ext = temp
            if config.has_option("options", "debug"):
                temp = config.get("options", "debug")
                if temp != "":
                    debug_mode = True
            if config.has_option("options", "flog"):
                temp = config.get("options", "flog")
                if temp != "":
                    save_ffmpeg_output = True

            # Advance the index an extra step, skipping the next since it's a
            # parameter.
            index += 1


        # Filename extensions
        elif argument.lower() == "-e":

            # Sanity check - is there a trailing argument?
            if index + 1 >= len(sys.argv):
                print("Missing argument - please check your command line.")
                quit()

            # Fetch the next argument, which SHOULD be the list of filename
            # extensions.
            temp = sys.argv[index + 1]

            # We've passed the sanity check, so let's store this argument.
            file_exts = temp.split(',')

            # Advance the index an extra step, skipping the next since it's a
            # parameter.
            index += 1


        # Output container
        elif argument.lower() == "-c":

            # Sanity check - is there a trailing argument?
            if index + 1 >= len(sys.argv):
                print("Missing argument - please check your command line.")
                quit()

            # Fetch the next argument, which SHOULD be the container.
            temp = sys.argv[index + 1]

            # We've passed the sanity check, so let's store this argument.
            new_ext = temp

            # Advance the index an extra step, skipping the next since it's a
            # parameter.
            index += 1


        # Debug mode enable
        elif argument.lower() == "-debug":

            # We've passed the sanity check, so let's store this argument.
            debug_mode = True


        # ffmpeg logging mode enable
        elif argument.lower() == "-flog":

            # We've passed the sanity check, so let's store this argument.
            save_ffmpeg_output = True


        elif argument.lower() == "--help":

            #      12345678901234567890123456789012345678901234567890123456789012345678901234567890
            print("This script monitors a selected directory and hands video files")
            print("to ffmpeg for transcoding into specific formats. it is designed")
            print("to serve as an ingest/export autoprocessor for transcoding")
            print("video files into and out of suitable formats for video editing.")
            print("")
            print("Usage:")
            print("  {} TRANSCODE [OPTIONS ...] -s /full/source/path "
                  "-d /full/dest/path [-f /full/finished/path] "
                  "[-ffmpeg /full/path/to/ffmpeg]"
                  . format(os.path.basename(__file__)))
            print("")
            print("Path Settings:")
            print("")
            print(" NOTE 1: These can appear in any order, but the parameter must")
            print(" immediately follow the switch.")
            print("")
            print(" NOTE 2: Paths that include spaces must be enclosed in double-quotes.")
            print("")
            print("  -s /full/source/path     : Full path to source files.")
            print("  -d /full/dest/path       : Full path to destination for transcodes.")
            print("  [-f /full/finished/path] : Full path to destination for storing")
            print("                             originals once transcodes have finished.")
            print("                             NOTE: If this is not provided, original")
            print("                             files will be renamed to end in '.processed'")
            print("                             when transcodes are finished.")
            print("  [-ffmpeg /full/path/to/ffmpeg] : Full path to ffmpeg - only needed")
            print("                             if ffmpeg is not in a directory on the")
            print("                             system's PATH.")
            print("  [-conf /full/path/to/config.ini] : Full path to configuration file.")
            print("                             File must be in INI format and overrides")
            print("                             commandline arguments.")
            print("")
            print("TRANSCODE Choices:")
            print("")
            print(" -davinci : Transcode to a format compatible with the Linux version")
            print("            of Davinci Resolve 16+ - MPEG4 video, PCM16LE audio,")
            print("            max quality, Quicktime MOV container.")            
            print("            These files can be big (~500MB/minute), so plan accordingly.")
            print(" -youtube : Transcode to a format that makes for small uploadable")
            print("            files for Youtube, based on Youtube's guidelines for")
            print("            transcoding as of 15 Dec 2020 - H.264 video, AAC audio.")
            print(" -dnxhr   : Transcode to Avid DNxHR HQ format, which is a highly")
            print("            intechangeable professional editing format that works")
            print("            with a variety of NLEs. WARNING: PRODUCES VERY LARGE")
            print("            FILES.")
            print(" -prores  : Transcodes to Apple ProRes 4444, which is a highly")
            print("            intechangeable professional editing format that works")
            print("            with a variety of NLEs. WARNING: PRODUCES VERY LARGE")
            print("            FILES.")
            print(" -plexhd  : Transcodes to a format that streams well over Plex,")
            print("            without requiring additional server-side transcoding.")
            print("            Files are scaled to 1080p, framerate is scaled to 30FPS,")
            print("            and videos with aspect ratios other than 16x9 are either")
            print("            letterboxed or pillarboxed to fit a 16x9 display.")
            print(" -plexsd  : Transcodes to a format that streams well over Plex.")
            print("            without requiring additional server-side transcoding.")
            print("            Files are scaled to 720p, framerate is scaled to 30FPS,")
            print("            and videos with aspect ratios other than 16x9 are either")
            print("            letterboxed or pillarboxed to fit a 16x9 display.")
            print(" -webm    : Transcode to WebM (VP9) constant-quality mode, which is")
            print("            a popular mode for image hosting sites that support")
            print("            short animations.")
            print("")
            print("Transcode Container OPTIONS:")
            print("")
            print(" -c [CONTAINER] : Container (filename extension) to transcode into,")
            print("                  'mp4' for MPEG4, 'mov' for Quicktime, 'mkv' for")
            print("                  Matroska, etc. This is automatically set for")
            print("                  transcode presets (-davinci, -youtube, etc.).")
            print("")
            print("Monitoring OPTIONS:")
            print("")
            print(" -e [EXTENSIONS] : Monitor source directory for specific filename")
            print("                   extensions. May be a list but entries must be comma-")
            print("                   separated and do not include periods, e.g., 'mp4,mov'.")
            print("                   By default, the most common video file extensions")
            print("                   supported by ffmpeg are selected.")
            print("")
            print("Debugging OPTIONS:")
            print("")
            print(" --help : Shows this text.")
            print(" --version : Shows version/Copyright information.")
            print(" -debug : Enable debug logging - all STDOUT is also copied to a")
            print("          log file.")
            print(" -flog  : Enable ffmpeg output logging - all ffmpeg output is")
            print("          copied to a log file. NOTE: This log file can become")
            print("          pretty large over time.")
            print("")
            quit()


        else:
            # Something got passed to the script that we don't recognize.
            print("Unrecognized option - please check your command line.")
            quit()


        # Advance the index.
        index += 1

else:
    print("No parameters given. Follow with '--help' for usage information.")
    quit()


# Sanity checks - let's make sure we have some settings.
if source_dir == '':
    print("No source directory - please check your command line or config file.")
    quit()
if dest_dir == '':
    print("No destination directory - please check your command line or config file.")
    quit()
if cmdline == []:
    print("No transcode mode selected - please check your command line or config file.")
    quit()
if new_ext == '':
    print("No container selected - please check your command line or config file.")
    quit()


# More sanity checking - let's make sure we can access programs we need to access.
if os.name == 'nt':
    if shutil.which(ffmpeg_location) is None:
        print("Program 'ffmpeg' not found or not on system's PATH - install the "
              "application package 'ffmpeg' to install it. Or, use the '-ffmpeg' "
              "argument to provide a full path to ffmpeg.exe.")
        quit()
else:
    if shutil.which(ffmpeg_location) is None:
        print("Program 'ffmpeg' not found or not on system's PATH - install the "
              "package 'ffmpeg' to install it. Or, use the '-ffmpeg' "
              "argument to provide a full path to ffmpeg.")
        quit()
    if shutil.which("fuser") is None:
        print("Program 'fuser' not found or not on system's PATH - install the "
              "package 'psmisc' to install it.")
        quit()


# Even more sanity checking - check to ensure we have write access to the
# destination directory.
try:
    with open(os.path.join(dest_dir, "check.tmp"), 'w') as check_file:
        pass
    os.remove(os.path.join(dest_dir, "check.tmp"))
except:
    print("Can't write to destination directory - please check your command line "
          "or config file, and if it is correct, make sure it's writable by "
          "root/sudo/admin accounts.")
    quit()


# Check to see if we have elevated privileges.
# Hat tip: "tahoar" at https://stackoverflow.com/questions/2946746/
if os.name == 'nt':
    try:
        # Try to pull a directory listing of the Windows TEMP directory, which
        # requires administrator rights.
        temp = os.listdir(os.sep.join([os.environ.get('SystemRoot','C:\\windows'),'temp']))
    except:
        print("This script must be run with elevated privileges. Aborting.")
        quit()

else:
    # Check to see if the current users is in the sudoers list and running the
    # script as root.
    #
    # NOTE: This will require "sudo" even when running in a root shell!
    if (not 'SUDO_USER' in os.environ) or (os.geteuid() != 0):
        print("This script must be run with elevated privileges. Aborting.")
        quit()


# Candidate file list
candidates = []

# Command line for each file
this_cmdline = []

# Progress bar length
bar_length = 40

# Loop delay time (seconds)
loop_delay = 5

# Start time for ETA estimation
start_time = 0

# Throbber text for progress bar
if os.name == 'nt':
    throbber = [
        "[*.   ]",
        "[.*.  ]",
        "[ .*. ]",
        "[  .*.]",
        "[   .*]",
        "[  .*.]",
        "[ .*. ]",
        "[.*.  ]",
        "[*.   ]"
    ]
else:
    throbber = [
        "[\033[93m*\033[33m*\033[0m   ]",
        "[\033[33m*\033[93m*\033[33m*\033[0m  ]",
        "[ \033[33m*\033[93m*\033[33m*\033[0m ]",
        "[  \033[33m*\033[93m*\033[33m*\033[0m]",
        "[   \033[33m*\033[93m*\033[0m]",
        "[  \033[33m*\033[93m*\033[33m*\033[0m]",
        "[ \033[33m*\033[93m*\033[33m*\033[0m ]",
        "[\033[33m*\033[93m*\033[33m*\033[0m  ]"
    ]

# Throbber step for progress bar
throbber_step = 0


# Helper REGEXes for transcode progress
# Hat tip: Werner Robitza :: https://gist.github.com/slhck
dur_regex = re.compile(
    r"Duration: (?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})\.(?P<ms>\d{2})"
)
time_regex = re.compile(
    r"out_time=(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})\.(?P<ms>\d{2})"
)


# Helper function for logging
def write_log(log_text, level='INFO'):

    # Print the log text to the screen.
    if __name__ == "__main__":
        print("[{0: <5}] {1}" . format(level, log_text))

    # Save to a log file.
    if debug_mode == True:
        with open(os.path.join(path, os.path.basename(sys.argv[0]) + ".log"), 'a') as log_file:
            log_file.write("[{0: <5}] {1}\n" . format(level, log_text))


# Helper function for converting timestamps to ms
# Hat tip: Werner Robitza :: https://gist.github.com/slhck
def to_ms(s=None, des=None, **kwargs) -> float:

    if s:
        hour = int(s[0:2])
        minute = int(s[3:5])
        sec = int(s[6:8])
        ms = int(s[10:11])
    else:
        hour = int(kwargs.get("hour", 0))
        minute = int(kwargs.get("min", 0))
        sec = int(kwargs.get("sec", 0))
        ms = int(kwargs.get("ms", 0))

    result = (hour * 60 * 60 * 1000) + (minute * 60 * 1000) + (sec * 1000) + ms
    if des and isinstance(des, int):
        return round(result, des)
    return result


# Helper function for creating a neat-looking progress bar
def progress_bar(percentage):

    # Sanity check - percentage must be 0..100
    # NOTE: Sometimes transcodes will exceed 100%.
    if percentage < 0:
        percentage = 0
    if percentage > 100:
        percentage = 100


    # Calculate how much of a progress bar should be shown based on the
    # percentage value.
    block = int(round(bar_length * (percentage / 100)))

    # Make an empty holder for the remaining time text.
    remaining_time = '??:??:??'

    # Calculate an ETA based on (current time - start time) extrapolated to 100%
    # but don't bother if we're below 10% as the calculation will be largely
    # meaningless in the early part of the job.
    if percentage >= 10:

        # Get the current time, then the difference from start.
        current_time = datetime.datetime.now()
        time_diff = current_time - start_time

        # Calculate ETA (well, est. time remaining) from time thus far and
        # percentage complete.
        total_time = (time_diff.total_seconds() * 100) / percentage
        eta = total_time * ((100 - percentage) / 100)

        # Break the ETA down into days/hours/mins/secs, and build display
        # text based on the results.
        (days, remainder) = divmod(eta, 86400)
        (hours, remainder) = divmod(remainder, 3600)
        (minutes, seconds) = divmod(remainder, 60)   
        days = int(days)
        hours = int(hours)
        minutes = int(minutes)
        seconds = int(seconds)
        if eta > 86400:
            remaining_time = ("{}:{:02d}:{:02d}:{:02d}  "
                              . format(days, hours, minutes, seconds))
        elif eta > 3600:
            remaining_time = ("{}:{:02d}:{:02d}  "
                              . format(hours, minutes, seconds))
        elif eta > 60:
            remaining_time = "00:{:02d}:{:02d}  " . format(minutes, seconds)
        else:        
            remaining_time = "{}s     " . format(seconds)

    # Fetch the global throbber step var - we're using a global so it retains
    # its value outside this function.
    global throbber_step


    # Build the progress bar. (The "\033[?25l" at the end turns the cursor off
    # so it doesn't blink at the end of the bar.)
    if os.name == 'nt':
        bar_text = ("{0}    [{1}{2}] : {3:0.2f}% / {4}" 
                    . format(throbber[throbber_step],
                             "#" * block,
                             "-" * (bar_length - block),
                             percentage,
                             remaining_time))
    else:
        bar_text = ("{0}    [\033[42m{1}\033[0m{2}] : {3:0.2f}% / {4}\033[?25l" 
                    . format(throbber[throbber_step],
                             ">" * block,
                             "-" * (bar_length - block),
                             percentage,
                             remaining_time))

    # Handle throbber text, which is basically changing a step counter.
    throbber_step += 1
    if throbber_step >= len(throbber):
       throbber_step = 0

    # We're done, so return the completed progress bar.
    return bar_text


# Helper function - check to see if a file is being used by another process.
def file_is_in_use(file):

    # We'll take one of two approaches to this, depending on the platform.

    if os.name == 'nt':

        # For Windows, we'll try to rename the file to the same name. If it
        # fails with an error, e.g., access-denied, something's working on/with
        # the file.
        try:
            os.rename(file, file)
            return False
        except:
            return True

    else:

        # For Linux, we'll invoke "fuser" with the "-u" switch to see what
        # users are accessing the file.
        is_file_open = subprocess.Popen(
            ['fuser -u "' + os.path.join(source_dir, file) + '"'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=False,
            shell=True,
        )
        file_users = is_file_open.stdout.read().decode("utf8", errors="replace").strip()

        return (file_users != "")


# Start the log...
write_log("", "INFO")
write_log("", "INFO")
write_log("", "INFO")
write_log("Automatic FFMPEG Transcoding Handler starting...", "INFO")
write_log(" * Transcode mode:", "INFO")
write_log("   {}" . format(trans_mode), "INFO")
write_log(" * Watching path:", "INFO")
write_log("   '{}'" . format(source_dir), "INFO")
write_log(" * Watching for the following file extensions:", "INFO")
write_log("   {}" . format(file_exts), "INFO")
write_log(" * Storing transcoded files in path:", "INFO")
write_log("   '{}'" . format(dest_dir), "INFO")
if storage_dir != '':
    write_log(" * Storing original files after transcoding in path:", "INFO") 
    write_log("   '{}'" . format(storage_dir), "INFO")
else:
    write_log(" * Original files will have filename extensions changed after ", "INFO")
    write_log("   transcoding.", "INFO")
write_log("", "INFO")
write_log("Starting monitor loop...", "INFO")


# Wrap the endless loop in a try/except.
try:

    # The eternal loop!
    while (True):

        # Our loop will look for and enumerate files within the source directory
        # that end in one of the extensions we watch for. 

        # Clear the candidate list - we'll populate this in a moment.
        candidates.clear()

        # Start by grabbing a list of the source directory
        dir_contents = os.listdir(source_dir)

        # Enumerare the directory listing
        for file in dir_contents:

            # Check to see if the file matches one of our target file
            # extensions.
            file_name, file_ext = os.path.splitext(file)
            if file_ext.lower().strip('.') in file_exts:

                # Ooh, we found something!

                # Have we seen this file before?
                if file not in candidates:

                    # Nope, so let's add it.
                    candidates.append(file)


        # How 'bout we process what we found, assuming we found anything.
        if len(candidates) > 0:

            # Log what we're doing. This is here instead of up above the line
            # that lists the source directory contents so it'll only trigger
            # if we find files to process. This helps keep the debug logs from
            # unnecessarily getting too big.
            write_log("", "INFO")
            write_log("Updating directory listing...", "INFO")

            # How many candidates did we find?
            write_log("... Done. {} transcoding candidate files found." 
                      . format(len(candidates)), "INFO")

            # Time to do work.
            write_log("Processing transcoding candidate files...", "INFO")

            for file in candidates:

                write_log("", "INFO")
                write_log(" Found file {} - checking..."
                          . format(file), "INFO")


                # Check to see if any process has the file open. If no users
                # have a claim on the file, let's do things with/to it.
                if not file_is_in_use(file):

                    # Note in the log that the file will be transcoded.
                    write_log("  Handing over to FFMPEG for transcode...", "INFO")

                    # Clear a var for progress monitoring
                    total_dur = None

                    # Prepare to make a copy of the command line list for this
                    # file.
                    this_cmdline.clear()

                    # Start with ffmpeg itself.
                    this_cmdline.append(ffmpeg_location)

                    # Split off the filename into root name and extension
                    # (we don't care about the extension).
                    file_name, _ = os.path.splitext(file)


                    # Build the command line by performing token replacement as
                    # required.
                    for entry in cmdline:

                        #entry = entry.replace("%FFMPEG%", ffmpeg_location)
                        entry = entry.replace("%SOURCEFILE%", '"' + os.path.join(source_dir, file) + '"')
                        entry = entry.replace("%DESTFILE%", '"' + os.path.join(dest_dir, file_name + "." + new_ext) + '"')
                        entry = entry.replace("%SPATH%", source_dir)
                        entry = entry.replace("%DPATH%", dest_dir)
                        entry = entry.replace("%NEWEXT%", new_ext)

                        this_cmdline.append(entry)

                    try:

                        # Clear the progress percentage variables.
                        prog_pct = 0
                        last_prog_pct = 0

                        # Reset the throbber step var.
                        throbber_step = 0

                        # Get the current time for estimating remaining time.
                        start_time = datetime.datetime.now()


                        # Open a log file if debug mode is enabled.
                        if save_ffmpeg_output == True:
                            f_log = open(os.path.join(path, "ffmpeg.log"), 'a')

                            # Start by writing the command line to the
                            # log, just in case inspecting it is needed.
                            f_log.write('Command line:\n')
                            f_log.write(" " . join(this_cmdline) + '\n\n')

                        # Launch ffmpeg
                        ffmpeg = subprocess.Popen(
                            " " . join(this_cmdline),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            universal_newlines=False,
                            shell=True,
                        )

                        # Loop until ffmpeg finishes.
                        while True:

                            # Grab a line of output from ffmpeg.
                            line = ffmpeg.stdout.readline().decode("utf8", errors="replace").strip()

                            # If the line is empty and poll() is no longer None,
                            # we're done.
                            if line == "" and ffmpeg.poll() is not None:
                                break                                

                            # Echo the line of text to the log.
                            if save_ffmpeg_output == True:
                                f_log.write(line.strip() + '\n')

                            # Check for progress info and derive a percent
                            # value of the transcode progress.
                            # Hat tip: Werner Robitza :: https://gist.github.com/slhck
                            if not total_dur and dur_regex.search(line):
                                total_dur = dur_regex.search(line).groupdict()
                                total_dur = to_ms(**total_dur)
                                continue
                            if total_dur:
                                result = time_regex.search(line)
                                if result:
                                    elapsed_time = to_ms(**result.groupdict())
                                    prog_pct = (elapsed_time / total_dur) * 100

                            # Update the progress, but only if it's changed.
                            if (prog_pct != last_prog_pct):
                                progress_bar_text = ("\r{}"
                                                     . format(progress_bar(prog_pct)))
                                sys.stdout.write(progress_bar_text)
                                sys.stdout.flush()
                                last_prog_pct = prog_pct


                        # Check for a non-zero return code (error) from ffmpeg.
                        if ffmpeg.returncode != 0:
                            if save_ffmpeg_output == True:
                                write_log("  Transcode failed. Check the ffmpeg"
                                          " output log for more information.",
                                          "ERROR")

                            else:
                                write_log("  Transcode failed. Enable ffmpeg "
                                          "output logging with -flog and retry "
                                          "for more information.",
                                          "ERROR")

                            # Quit so the transcode failure can be investigated.
                            sys.exit(0)


                        # Get the current time, then the difference from start.
                        current_time = datetime.datetime.now()
                        time_diff = current_time - start_time

                        # Create a blank variable for the total time the transcode
                        # took.
                        elapsed_time = ''

                        # Break the time difference down into days/hours/mins/secs,
                        # and build display text based on the results.
                        (days, remainder) = divmod(time_diff.total_seconds(), 86400)
                        (hours, remainder) = divmod(remainder, 3600)
                        (minutes, seconds) = divmod(remainder, 60)   
                        days = int(days)
                        hours = int(hours)
                        minutes = int(minutes)
                        seconds = int(seconds)
                        if time_diff.total_seconds() > 86400:
                            elapsed_time = ("{}:{:02d}:{:02d}:{:02d}"
                                              . format(days, hours, minutes, seconds))
                        elif time_diff.total_seconds() > 3600:
                            elapsed_time = ("{}:{:02d}:{:02d}"
                                              . format(hours, minutes, seconds))
                        elif time_diff.total_seconds() > 60:
                            elapsed_time = "00:{:02d}:{:02d}" . format(minutes, seconds)
                        else:        
                            elapsed_time = "{}s" . format(seconds)


                        # Write a little bit of whitespace to the log file
                        # and close it.
                        if save_ffmpeg_output == True:
                            f_log.write('\n\n\n')
                            f_log.close()


                        # Transcode complete!
                        sys.stdout.write('\n')
                        sys.stdout.flush()
                        write_log("  Transcode completed in {}."
                                  . format(elapsed_time), "INFO")

                        # Sleep 5 seconds for everything to settle.
                        time.sleep(5)


                    finally:
                        # Move the file to storage if a storage directory
                        # is provided. If not, rename the file.
                        if storage_dir != '':

                            # We'll be moving it.
                            write_log("  Moving source file to dir '{}'..." . format(storage_dir), "INFO")

                            # Do the thing!
                            os.rename(os.path.join(source_dir, file),
                                    os.path.join(storage_dir, file))

                        else:
                            # We'll be renaming it.
                            write_log("  Renaming source file...", "INFO")

                            # Do the thing!
                            os.rename(os.path.join(source_dir, file),
                                      os.path.join(source_dir, file + ".processed"))


                        # Sleep 5 seconds for file moves/renames to
                        # follow through.
                        time.sleep(5)

                        # Aaaaand done.
                        write_log("  Processing complete.", "INFO")

                        # Pad out the log with an empty line.
                        write_log("", "INFO")


                else:
                    # Note in the log that this is an ongoing observation.
                    write_log(" File is still in use or being transferred - skipping for now...", "INFO")


            # Throw a little time delay into the iteration.
            time.sleep(loop_delay)


            # Aaand we're done for now.
            write_log("... Done.", "INFO")


        # Sleep for a bit before doing it all again.
        time.sleep(loop_delay)

except SystemExit:
    write_log("Exiting.", "INFO")

    # The "\033[?25h" turns the cursor back on so the terminal has a cursor
    # when the script exits. This is only needded on Linux.
    if os.name != 'nt':
        write_log("\033[?25h", "ERROR")

    # Exit normally.
    sys.exit(0)

except KeyboardInterrupt:
    write_log("Exiting.", "INFO")

    if os.name != 'nt':
        write_log("\033[?25h", "ERROR")

    # Exit normally.
    sys.exit(0)


except:
    # Log the error.
    write_log("*** ERROR!", "ERROR")
    write_log(traceback.print_exc(), "ERROR")
    if os.name != 'nt':
        write_log("\033[?25h", "ERROR")

    # Exit abnormally.
    sys.exit(1)


# END!
