# pythonmisc/gobject -- Experimentation with GObject introspection

I've been playing around with using GObject introspection to do some things:

* driving GStreamer
* building GTK GUIs
* using Clutter to make dynamic and animated layouts

In some of the files here I'm also using asyncio, with gbulb providing the
actual interface between asyncio and the GLib main event loop.

Assumptions:

* Python 3.4
* PyGObject is installed
* gbulb is installed


## Notes about installing GObject

This was awkward, espcially to install into a virtualenv. In the end, this is
what seemed to work for me:

    $ wget http://ftp.gnome.org/pub/GNOME/sources/pygobject/3.10/\
        pygobject-3.10.2.tar.xz
    $ tar xaf pygobject-3.10.2.tar.xz
    $ cd pygobject-3.10.2
    $ workon my_environment
    $ ./configure --with-python=`which python` --prefix=$VIRTUAL_ENV
    $ make clean all install


