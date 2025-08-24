
import os
from django import template

from imagine.models import Folder,File

register = template.Library()

##### Not used ######################3
@register.simple_tag
def identify_by_name(name):
    # Check for file extension
    if '.' in name:
        # It looks like a file, check in the File model
        file = File.objects.filter(fname=name).first()
        if file:
            return "file"
    else:
        # It doesn't have an extension, check in the Folder model
        folder = Folder.objects.filter(name=name).first()
        if folder:
            return "folder"
    
    return "Not found"


#### Returning  file extension name of a file, used by all the display page ############
@register.filter
def file_extension(filename):

    return os.path.splitext(filename)[1][1:]  # Returns the file extension without the dot



#### Returning folder path list of a objects, used by all the display page ############
@register.filter
def back_history(parent_id):
    try:
        parent = Folder.objects.get(data_id=parent_id)
    except:
        return ['None']  # If no parent is found, return 'None'

    parent_list = []
    
    # Traverse up the parent chain until reaching 'Home'
    while parent and parent.name != 'Home':
        parent_list.append(parent)
        parent = parent.parent  # Assuming parent is a ForeignKey to Folder
    
    parent_list.reverse()

    # Limit to the last 5 items
    if len(parent_list) > 5:
        parent_list = parent_list[-5:]

    # If no parents were found, return 'None'
    if not parent_list:
        return ['None']
    
    return parent_list


#### Returning folder path list of a objects, used by all the Share.html and share-working.html page ###########
@register.filter
def back_history_sharing(parent_id,parent_name):
    base_fd = Folder.objects.get(data_id=parent_id)
    current_fd = Folder.objects.get(name=parent_name)
    super_parent = current_fd.parent
    parent_list = []
    while base_fd.name != super_parent.name:
        parent_list.append(base_fd)
        base_fd = base_fd.parent 
        # Assuming parent is a ForeignKey to Folder   
  
    parent_list.reverse()
    if len(parent_list) > 5:
        parent_list = parent_list[-5:]
  
    return parent_list


#### Returning folder instance by using data_id used b the Share-working.html page ############
@register.filter
def get_folder_intance(parent_id):
        parent = Folder.objects.get(data_id=parent_id)
        print(parent.folderuser, ' this is  get folder instance')
        return parent



#### Returning Short name for the user, uses by all the display pages ############
@register.filter
def get_short_uname(name):
    result = name.split(" ")

    list=result[0][0]
    list= list + result[1][0]
    return list.upper()



### Returning filesize_in_kb(value) by using data_id used by all the display page ############
@register.filter
def filesize_in_kb(value):
    """Converts bytes to MB (Megabytes)."""
    try:
        if value is None:
           return "0 MB"
        mb_value = value /(1024 * 1024)
        return f"{mb_value:.2f} MB"
    except:
        return f"{0:.2f} MB"
    


#### Returning itemcount inside a folder by using data_id used by all the display page ############
@register.filter
def item_counts(object_id):
    parent = Folder.objects.get(data_id=object_id)
    files = File.objects.filter(folder=parent)
    folders = Folder.objects.filter(parent=parent)
    count = files.count() + folders.count()
    return count



#### Returning the pathlist of a object by using data_id used by all the Trash.html page  for displaying the original path ############
@register.filter
def path_list(id):
    list =""
    try:
        parent = Folder.objects.get(data_id=id)
    except:
        parent = File.objects.get(data_id=id)

    if list != None:
        try:
            while parent.name != 'Home':
                list = list + '/'+ parent.name
                parent = parent.parent
            list = list.split('/')
            list.reverse()
            list = ('/').join(list)
            list = 'Home' + '/' + list
            return list
        except:
             list='None'
             return list
    else:
        return list


#### Returning file instance by using data_id used b the Trash.html page for getting the file attributes ############
@register.filter
def get_obj_inst(obj_id):
  
   
    file = File.objects.get(data_id=obj_id)
  
    return file





    
  

    