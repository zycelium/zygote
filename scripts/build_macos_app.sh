#!/bin/sh

python setup.py py2app


if [ ! -d "dist/Zygote.app" ]; then
    echo "py2app failed."
    exit 1
fi

# Remove the old app
rm -rf "Zygote.app"
mv "dist/Zygote.app" .

# Remove the build directory
rm -rf {dist,build} 
