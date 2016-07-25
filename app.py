import arrow
import json
from flask import Flask, request, jsonify, abort

from peewee import *

DATABASE = "weather_data.db"
DEBUG = False
SECRET_AUTH_KEY = "secret key"

app = Flask(__name__)
app.config.from_object(__name__)

# create a peewee database instance -- our models will use this database to
# persist information
database = SqliteDatabase(DATABASE)


class BaseModel(Model):
    class Meta:
        database = database


class DHTData(BaseModel):
    timestamp = DateTimeField()
    temp_c = FloatField()
    temp_f = FloatField()
    humidity = FloatField()
    hic = FloatField()
    hif = FloatField()


def update_data_file():
    data_template = {
        'last_48h': [],
        'humidity_48h': [],
        'temperature_48h': [],
        'temperature_current_c': 'N/A',
        'temperature_current_f': 'N/A',
        'humidity_current': 'N/A',
        'heat_index_current': 'N/A',
        'temperature_c_last_20': [],
        'temperature_f_last_20': [],
        'humidity_last_20': [],
        'heat_index_last_20': []
    }

    for d in reversed(DHTData.select().order_by(-DHTData.id).limit(20)):
        data_template['temperature_c_last_20'].append(d.temp_c)
        data_template['temperature_f_last_20'].append(d.temp_f)
        data_template['humidity_last_20'].append(d.humidity)
        data_template['heat_index_last_20'].append(d.hic)

    last = DHTData.select().order_by(DHTData.id.desc()).get()

    data_template['temperature_current_c'] = str(last.temp_c)
    data_template['temperature_current_f'] = str(last.temp_f)
    data_template['humidity_current'] = str(last.humidity)
    data_template['heat_index_current'] = str(last.hic)

    start = arrow.utcnow().replace(hours=-48).to("Europe/Berlin")
    end = arrow.utcnow().to("Europe/Berlin")

    for h in arrow.Arrow.span_range('hour', start, end):
        dt_start = h[0]
        dt_end = h[1]
        data_template['last_48h'].append(dt_start.format('HH'))
        c_temp_points = []
        humidity_points = []
        query = DHTData.select().where(DHTData.timestamp.between(dt_start.datetime,
                                                                 dt_end.datetime))

        for point in query:
            c_temp_points.append(point.temp_c)
            humidity_points.append(point.humidity)

        if c_temp_points:
            data_template['temperature_48h'].append(round(sum(c_temp_points) / len(c_temp_points), 2))
        else:
            data_template['temperature_48h'].append(None)

        if humidity_points:
            data_template['humidity_48h'].append(round(sum(humidity_points) / len(humidity_points), 2))
        else:
            data_template['humidity_48h'].append(None)

    with open("js/data.js", "w") as out:
        out.write("var data=" + json.dumps(data_template))


@app.route('/api/v1/update/', methods=['POST'])
def store_data():
    data = request.form
    if data.get('key') != SECRET_AUTH_KEY:
        abort(404)

    dht_object = DHTData(timestamp=arrow.utcnow().to("Europe/Berlin").datetime,
                         temp_c=float(data.get('celsius', 0)),
                         temp_f=float(data.get('fahrenheit', 0)),
                         humidity=float(data.get('humidity', 0)),
                         hic=float(data.get('hic', 0)),
                         hif=float(data.get('hif', 0))
                         )
    dht_object.save()

    if arrow.utcnow().minute in range(0, 60, 2):
        update_data_file()

    return jsonify({'results': 'OK'})


if __name__ == '__main__':
    DHTData.create_table(fail_silently=True)
    app.run(host='0.0.0.0')
