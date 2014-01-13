from os.path import exists

def notify(title, subtitle, message):
    from os import system
    t = '-title {!r}'.format(title)
    s = '-subtitle {!r}'.format(subtitle)
    m = '-message {!r}'.format(message)
    a = '-sender {!r}'.format("com.typemytype.robofont")
    system('terminal-notifier {}'.format(' '.join([m, t, s, a])))

if exists("/usr/bin/terminal-notifier"):
    use_notifications = True
else:
    use_notifications = False
    print "In order to use notifications, install the command line program with:"
    print "$ sudo gem install terminal-notifier"

if use_notifications:
    notify("Hello from RoboFont", "Hello", "World")