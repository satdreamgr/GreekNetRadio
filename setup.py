from distutils.core import setup

pkg = 'Extensions.GreekNetRadio'
setup (name = 'enigma2-plugin-extensions-greeknetradio',
       version = '1.0',
       description = 'Greek web radios',
       package_dir = {pkg: 'plugin'},
       packages = [pkg],
       package_data = {pkg: ['*stations', 'buttons/*.png', 'icons/*.png',
                             'flex.sh', 'po/el/LC_MESSAGES/lang.*', 'greekradio.png']},
      )

