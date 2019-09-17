import pip._internal as pip

'pip install --editable .'
pip.main(['install', '--proxy=10.100.10.201:8080', '--editable', '.'])
