import os

from app import app, DHTData

if __name__ == '__main__':
    DHTData.create_table(fail_silently=True)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
