# Anicollage

Script for making animated collages

## Requirements
- `python`
- `dvd-slideshow`
- `av-conv`

## Generate the collage animation
```
./anicollage.py image.png outdir
```

dir2slideshow -t 0.2 collage

## Generate the slideshow

```
dvd-slideshow -f collage.txt
```

## Convert slideshow to mp4
```
avconv -i slideshow.vob -c:v copy -an slideshow.mp4
```
