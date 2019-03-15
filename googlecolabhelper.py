import os
import re

class GoogleColabHelper(object):
  '''
  Purpose: Make life easier for Stephen.
   
  Usage:   
  !rm -frv googlecolabhelper
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
  '''
  
  def __init__(self,additional_libraries=[],extract_zips=[],*args,**kwargs):
    assert self.__is_google_colab(),"This module only applies for use in Google Colaboratory"
      
    self.additional_libraries = additional_libraries
    self.extract_zips = extract_zips
    
    self.required_libraries = [
      'Cython','numpy','spacy','gensim',
      'torch','sklearn','pandas','matplotlib',
      'line-profiler','tensorboardx'
    ]
    
    # Constants
    self.GDRIVE_MOUNTPOINT = '/content/gdrive'

    self.MYDRIVE_LOCATION = '/content/gdrive/My Drive'
    self.MYDRIVE_MOUNTPOINT = '/content/mydrive'

    self.COLAB_LOCATION = '/content/gdrive/My Drive/Colab Notebooks'
    self.COLAB_MOUNTPOINT = '/content/notebooks'

  ########################### PRIVATE METHODS ###########################
  
  def __is_google_colab(self,*args,**kwargs):
    try:
      import google.colab.errors
      return True
    except:
      return False
      
  # Run IPython magic
  # Usage: run_ipython_magic('time')    # calls '%time' to show timing info
  # Usage: run_ipython_magic('sx','ls') # calls '%sx ls' to run a shell command
  def __run_ipython_magic(self,magic,params='',filter_out=None):
    from IPython.terminal.embed import InteractiveShellEmbed
    ipshell = InteractiveShellEmbed()
    ipshell.dummy_mode = False
    
    try:
      print("%{} {}".format(magic,params))
      o=ipshell.run_line_magic(magic,params)
    except Exception as e:
      print("Failed to run IPython magic: %{} with parameters: {}".format(magic,params))
      raise e

    # Some commands output directly (e.g. %time), some return the output (e.g. %sx) - it's weird
    if(o):
      for l in o:
        if filter_out:
          if re.search(filter_out,l):
            continue
            
        print(l)
 
  def __unzip_file(self,zip_path,target_path=None,exclude_list=None):
    
    target_option = ""
    if target_path:
      target_option = ' -d "{}"'.format(target_path)
      
    exclude_option = ""
    if exclude_list != None and isinstance(exclude_list,list):
      exclude_option = ' '.join(['-x "{}"'.format(x) for x in exclude_list])
      
    zip_cmd = 'unzip -u "{}" {} {}'.format(zip_path,target_option,exclude_option)
    self.__run_ipython_magic('sx',zip_cmd)
 
  ########################### PUBLIC METHODS ###########################

  def prepare(self,*args,**kwargs):
    self.mount_gdrive() # Mount and map to /content/gdrive
    self.mount_mydrive() # Mount and map to /content/mydrive
    self.mount_notebooks() # Mount and map /content/notebooks
    self.install_libraries() # Install required + any additional libraries
    self.extract_zip_files() # Extract any specified ZIPs
    
  def mount_gdrive(self,*args,**kwargs):
    print("Mounting Google Drive to {}".format(self.GDRIVE_MOUNTPOINT))
    try:
      from google.colab import drive
      drive.mount(self.GDRIVE_MOUNTPOINT)
      return True
    except Exception as e:
      print("Unable to mount GDrive")
      raise e
    
  def mount_mydrive(self,*args,**kwargs):
    print("Mounting My Drive to {}".format(self.MYDRIVE_MOUNTPOINT))
    
    cmd = 'sudo ln -sf "{}" "{}"'.format(self.MYDRIVE_LOCATION,self.MYDRIVE_MOUNTPOINT)
    self.__run_ipython_magic('sx',cmd)
     
  def mount_notebooks(self,*args,**kwargs):
    print("Mounting Notebooks to {}".format(self.COLAB_MOUNTPOINT))
    
    cmd = 'sudo ln -sf "{}" "{}"'.format(self.COLAB_LOCATION,self.COLAB_MOUNTPOINT)
    self.__run_ipython_magic('sx',cmd)
    
  def install_libraries(self,*args,**kwargs):
    try:
      libraries_to_install = self.required_libraries # default
      libraries_to_install.extend(self.additional_libraries) # optional
      
      library_list = ' '.join(libraries_to_install)
      cmd = 'pip install ' + library_list
      self.__run_ipython_magic('sx',cmd,"Requirement already satisfied:")
      
    except Exception as e:
      print("Failed to pip install libraries.")
      raise e
    
  def extract_zip_files(self,*args,**kwargs):
    zip_error_msg = "extract_zip specification must be a dictionary with keys: name, source, zip, target_path"
    for z in self.extract_zips:
      assert isinstance(z,dict), zip_error_msg
      assert z.get('name'), zip_error_msg
      assert z.get('source'), zip_error_msg
      assert z.get('zip'), zip_error_msg
      assert z.get('target_path'), zip_error_msg
      
      print("Extracting ZIP: {}".format(z.get('name')))
      self.__unzip_file(
        zip_path=os.path.join(z.get('source'),z.get('zip')),
        target_path = z.get('target_path'),
        exclude_list = z.get('exclude_list') # optional
      )