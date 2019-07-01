import signal
from jinshuju_viewer import app, utils
signal.signal(signal.SIGINT, utils.handlerSIGINT)
app.run(host="0.0.0.0", port="5001")