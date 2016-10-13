#NodeMCU/Raspberry pi + DHT22 Sensor reading and data dashboard

## Dashboard

The dashboard is using flask, it also contains Procfile for easy deployment. All the requirements for the dashboard/API server are listed in the requirements.txt file. Tested with sqlite and postgresql, it will default to sqlite if no database is defined.

To specify database set the `DEFAULT_DATABASE` environment variable e.g. `export DEFAULT_DATABASE="postgresql://postgres:postgres@localhost/postgres"`

Make sure you set your `SECRET_AUTH_KEY` env variable the same way to something unique.

## Raspberry pi requirements

* Adafruit Python DHT Sensor Library - installation instructions: https://github.com/adafruit/Adafruit_Python_DHT

* requests library - run `pip install requests`

To specify API URL and the secret key you can either use the environment variables `PI_STATION_API` and `PI_STATION_SECRET_AUTH_KEY` respectively. Or you can edit the `pi_station.py` file and hardcode those values.

## Screenshot

![safari_screenshot](screenshot_2016-07-25.png?raw=true)

Live demo: http://temperature.nikolak.com/

## License

The MIT License (MIT)

Copyright (c) 2016 Nikola Kovacevic

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
