from distutils.core import setup

pkg = 'Extensions.GreekNetRadio'
setup (name = 'enigma2-plugin-extensions-greeknetradio',
       version = '3.0',
       description = 'Internet radio by SatDreamGr',
       package_dir = {pkg: 'plugin'},
       packages = [pkg],
       package_data = {pkg: ['*stations', 'flex.sh', 'po/el/LC_MESSAGES/lang.*', 'greekradio.png']},
)
