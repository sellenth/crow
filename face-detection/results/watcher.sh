#!/bin/bash

while read j
do
  eog ./new0.jpg & eog ./new1.jpg & eog ./new2.jpg & eog ./new3.jpg
done <  <(inotifywait -q -e modify ./new0.jpg)
