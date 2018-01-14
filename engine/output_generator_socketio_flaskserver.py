import tensorflow as tf
from flask import stream_with_context, request, Response, Flask
from flask_socketio import SocketIO, send, emit
from engine.realtime_VideoStreamer import VideoStreamer
from engine.realtime_RecognitionEngine_textOutput import RecognitionEngine
from keras.models import load_model
from engine.realtime_VideoStreamer import VideoStreamer
from keras import backend as K

from engine.realtime_RecognitionEngine_textOutput_v2_copy import RecognitionEngine

# emotion_model_path = './Engine/trained_models/emotion_models/fer2013_mini_XCEPTION.102-0.66.hdf5'
# emotion_classifier = load_model(emotion_model_path, compile=False)
# emotion_classifier._make_predict_function()
# graph = tf.get_default_graph()

app = Flask(__name__)
socketio = SocketIO(app, async_mode="threading", ping_timeout=10000)

#EXAMPLE LINK:
# http://0.0.0.0:8888/stream?links=https://www.twitch.tv/a541021,https://www.twitch.tv/lostaiming,https://www.twitch.tv/fps_shaka,https://www.twitch.tv/cawai0147&resolution=360p


streamer_list = []
# r_engine = RecognitionEngine(streamer_list,  emotion_classifier, graph, queueSize=128)

@socketio.on('connect')
def handle_connect():
    print("connected")
    emit('test', "test0")

@socketio.on('disconnect')
def handle_disconnect():
    K.clear_session()
    print("disconnected")

@socketio.on('sendStreamer', namespace='/stream')
def handle_top_five_streamer(arg1):

    K.clear_session()
    emit('session_clean', 'clean')

    tf.reset_default_graph()
    emotion_model_path = './Engine/trained_models/emotion_models/fer2013_mini_XCEPTION.102-0.66.hdf5'
    emotion_classifier = load_model(emotion_model_path, compile=False)
    emotion_classifier._make_predict_function()
    graph = tf.get_default_graph()
    emit('network_created', 'created_network')


    print('received args: ' + str(arg1))
    # emit("test", "test1")

    link_list = arg1
    resolution = '360p'


    video_streamer_list = []

    for link in link_list:
        vs = VideoStreamer("https://www.twitch.tv"+str(link), queueSize=128, resolution=resolution, n_frame=15)
        video_streamer_list.append([link, vs])

    r_engine = RecognitionEngine(video_streamer_list, emotion_classifier, graph, queueSize=128)
    # emit('test',"test2")
    while True:

        if r_engine.more():

            element = r_engine.read()
            text = "[" + str(element[0]) + "," + str(element[1]) + "]"
            print(text)
            emit('rageIncoming', {'link': str(element[0]), 'confidence': str(element[1])})

        else:
            # emit('heart', {'link': "%no-rage", 'confidence': "0"})
            continue

if __name__ == '__main__':
    socketio.run(app)

    # app.run(debug = True, host='0.0.0.0', port=8888, passthrough_errors=True, threaded=True)