#!/bin/bash
for i in collage/*.png; do
    imgpath=`readlink -f $i`
    echo ${imgpath}:0.3
    echo crossfade:0.3
done
