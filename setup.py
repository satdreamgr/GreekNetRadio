from distutils.core import setup
import setup_translate

pkg = 'Extensions.GreekNetRadio'
setup (name = 'enigma2-plugin-extensions-greeknetradio',
       version = '3.1',
       description = 'Internet radio by SatDreamGr',
       package_dir = {pkg: 'plugin'},
       packages = [pkg],
       package_data = {pkg: ['*stations', 'flex.sh', 'greekradio.png']},
       cmdclass = setup_translate.cmdclass,
)
