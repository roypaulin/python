#!/bin/sh
#Genère une archive pour le rendu sans les fichiers ignorés et le .git
ARCHIVE=rendu.tar.gz
OWN_NAME=`basename "$0"`
rm $ARCHIVE
dirName=` echo "${PWD##*/}" `
destFullPath=` echo /tmp/$dirName/ `
rm -rf $destFullPath
rsync -av --progress `pwd` /tmp/ --filter=':- .gitignore' --exclude .git \
--exclude rapport.md --exclude $OWN_NAME --exclude $ARCHIVE
tar -zcvf $ARCHIVE -C /tmp/ $dirName
