# Image Scripts

A collection of command line scripts for image processing. Mostly with Bash, ImageMagick and FFMPEG.

## ImageMagick

- add background to transparent PNGs `mogrify -background "#FFFFFF" -flatten images/*.png`

## FFMPEG

- Convert image sequence to video: `ffmpeg -framerate 24 -pattern_type glob -i "input/*.png" -c:v libx264 -r 24 -pix_fmt yuv420p output.mp4`

## Bash

- zero pad `n=`printf %03d $n``