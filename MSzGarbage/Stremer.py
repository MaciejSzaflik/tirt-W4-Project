import os
import sys
import Tkinter as Tk

import gobject
import gst


class RootObject(object):

    def startPlaying(self):
        self.player.set_state(gst.STATE_PLAYING)
        return

    def stopPlaying(self):
        self.player.set_state(gst.STATE_PAUSED)
        return



    def on_sync_message(bus, message, window_id):
            if not message.structure is None:
                if message.structure.get_name() == 'prepare-xwindow-id':
                    image_sink = message.src
                    image_sink.set_property('force-aspect-ratio', True)
                    image_sink.set_xwindow_id(window_id)

    def __init__(self, parent):
        gobject.threads_init()
        self.root = parent
        self.root.title("Main frame")
        self.frame = Tk.Frame(parent)
        self.frame.pack()

        btn = Tk.Button( self.frame, text="Play", command=self.startPlaying)
        btn.pack(side=Tk.BOTTOM,anchor=Tk.W)
        btn2 = Tk.Button( self.frame, text="Stop", command=self.stopPlaying)
        btn2.pack()



        self.player = gst.element_factory_make('playbin2', 'player')
        self.player.set_property('video-sink', None)
        self.player.set_property('uri', 'file://%s' % (os.path.abspath(sys.argv[1])))
        video = Tk.Frame(self.root, bg='#000000')
        video.pack(side=Tk.BOTTOM,anchor=Tk.S,expand=Tk.YES,fill=Tk.BOTH)


        window_id = video.winfo_id()
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect('sync-message::element', self.on_sync_message, window_id)





if __name__ == "__main__":
    root = Tk.Tk()
    root.geometry("800x600")
    app = RootObject(root)
    root.mainloop()
