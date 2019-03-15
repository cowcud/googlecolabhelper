# googlecolabhelper
Make it easier to setup Google Colab environment

Usage:
   
  !rm -fr googlecolabhelper
  !git clone https://github.com/cowcud/googlecolabhelper.git
  from googlecolabhelper import *

  zips = [{
    'name':'models',
    'source':r'/content/gdrive/My Drive/modelframework/',
    'zip':'models20190315.zip',
    'target_path':r'/content/models/',
  }]
  
  colabenv = GoogleColabHelper(
    additional_libraries=['six','pyyaml'], extract_zips=zips
  )
  colabenv.prepare()