from ctypes import pythonapi
import io
import mimetypes
from platform import win32_ver
import zipfile
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import FolderForm
import os
from django.contrib.auth import authenticate,login,logout
# Model imports
from imagine.models import Folder,File, Trasher, UserFilePermission, UserFolderPermission
import io
from django.db.models import Q
from docx import Document





#############################  used to get the extation of a file name     ####################

def get_file_extension(request,filename):
    # Split the filename into the name and extension
    name,extension = os.path.splitext(filename)
    # Remove the leading dot from the extension
    print("inside get file extension")
    return extension.lower().lstrip('.') 

############################### get the file_id and name #############################

def get_object_details(request, object):
    if object:
        object_id = File.objects.get(data_id = object.data_id)
        object_name = File.objects.get(fname = object.fname)
        data = {
            'object_id': object_id,
            'file_name':  object_name,
        }
        return JsonResponse(data)
    
    messages.warning(request, f"File not found which you have asked for.")



 ##########################  Doc file to Docx converting ##############(though it did not workd) 

def convert_doc_to_docx_in_memory(file_path):
    pythonapi.CoInitialize()  # Needed to avoid multi-threading issues with COM objects
    word = win32_ver.Dispatch("Word.Application")
    word.Visible = False  # Hide the Word application
    
    doc = word.Documents.Open(file_path)
    docx_io = io.BytesIO()

    # Save as .docx to a memory stream
    doc.SaveAs(docx_io, FileFormat=16)  # 16 represents the Word .docx format
    doc.Close()
    word.Quit()




######################################################### This section is specifically for the Dashboard View ###############################################################################################


## The first Dashboard Display for the users, On the first login users dispaly provided from this view
def index(request, parent_id=None):
    if request.user.is_authenticated:
        print(parent_id)
        if parent_id:
            parent = Folder.objects.get(name='Home',data_id=parent_id)
            
        else:
            parent = Folder.objects.get(name='Home', folderuser=request.user)
        folder = Folder.objects.filter(folderuser=request.user,parent= parent.data_id)
        file = File.objects.filter(folder=parent)
        user_list = User.objects.exclude(id=request.user.id)
        print(user_list)
        context = {'folders': folder,'parent_name':'Home', 'files':file,'parent_id': parent.data_id, 'users': user_list}
     
        return render(request,'index.html',context)        
    else:
        return redirect('signup')


############################# Display Folder contents and Handles file uploads in Dashboard  #############################

def folder(request,parent_id,folderNm=None,type=None):
    if request.user.is_authenticated:
        parent_folder = Folder.objects.get(data_id=parent_id)
        home = Folder.objects.get(name='Home',folderuser=request.user)
        files = File.objects.filter(folder=parent_folder)
        folders=Folder.objects.filter(parent=parent_folder)
        user_list = User.objects.exclude(id=request.user.id)
        context = {'parent_id':parent_id,'files':files, 'folders':folders, 'parent_name':parent_folder, 'users': user_list}
        if request.method == 'POST':
            filelist = request.FILES.getlist('file')
            for file in filelist:
               name=(str(file))
               if not File.objects.filter(fname=name,folder=parent_folder,file=file).exists():
                  
                  fileadd = File.objects.create(fname=name,folder=parent_folder,file=file)
                  messages.success(request, f"File {(str(file))} uploaded successfully.")

               else:
                 messages.warning(request, f"File {(str(file))} already exists and was not uploaded.")
        if type:
            print('i have been called by copy that\' why i am here')
            context = {'parent_id':parent_id,'files':files, 'folders':folders, 'home':home,'parent_name':parent_folder, 'users': user_list} 
            return render (request, 'copy.html', context)
        if folderNm:
            print('i have been called that\' why i am here')
            context = {'parent_id':parent_id,'files':files, 'folders':folders, 'home':home,'parent_name':parent_folder, 'users': user_list} 
            return render (request, 'move.html', context)
        
        
        return render(request,'folder.html',context)
    else:
        return redirect('signup')
    


# ################################## search view display for Dashboard ############################

def search_view(request, parent_id):
    if request.user.is_authenticated:
        parent_folder = Folder.objects.get(data_id=parent_id)
        user_list = User.objects.exclude(id=request.user.id)
        query = request.GET.get('search_quary')  # Get the search term
        print(query)
        if query:
        # Filter the model (e.g., Folder) based on the search term
            result_folders = Folder.objects.filter(Q(name__contains=query) & Q(folderuser=request.user) & Q(is_deleted='No')).exclude(name='Trash')
            result_files = File.objects.filter(Q(fname__contains=query) & Q(folder__folderuser=request.user)& Q(is_deleted='No')).exclude(fname='Trash')
        else:
            result_folders = Folder.objects.none()
            result_files = File.objects.none()
        context = {'parent_id':parent_id,'files':result_files, 'folders':result_folders, 'parent_name':parent_folder, 'users': user_list}
        return render(request,'folder.html',context)
    else:
        return redirect('signup')

    
############################## Loding parent based on the request for Dashboard############################

def load_parent(request,parent_id):
    if request.user.is_authenticated:
        old_parent = Folder.objects.get(data_id=parent_id, folderuser=request.user)
        return redirect("folder", parent_id=old_parent.data_id)

    else:
        return redirect('signup')
    


#################################File_opening function for view for Dashboard ################################
def open_file(request,object_id):
    if request.user.is_authenticated:
        file_obj = get_object_or_404(File, data_id=object_id)

        content_type = 'application/octet-stream'
        disposition = 'attachment'  # Default to download for other file types
        
        type = get_file_extension(request,file_obj.fname)
        # Open the file and return it as a response
        with open(file_obj.file.path, 'rb') as object_file:
            
            content_type = 'application/pdf'
            disposition = 'inline'
            if type == 'pdf':
                content_type = 'application/pdf'
                disposition = 'inline'
            elif type in ['xlsx', 'xls']:
                content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                disposition = 'attachment'  # For Excel, force download
            elif type =='docx':
                content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                disposition = 'inline'  # For word files
            
            elif type ==['txt', 'bin', 'ps' , 'cmd']:
                content_type='text/plain'
                disposition = 'inline'
            elif type =='doc':
                docx_stream = convert_doc_to_docx_in_memory(file_obj.file.path)
                response = HttpResponse(docx_stream, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                response['Content-Disposition'] = f'inline; filename="{file_obj.fname}.docx"'
                return response
               
            elif type in ['jpg','jpeg','png', 'gif','bmp', ]:
                content_type, encoding = mimetypes.guess_type(file_obj.fname)
                content_type = content_type
                disposition = 'inline'  
            elif type == 'rar':
                content_type='application/x-rar-compressed'
                disposition = 'attachment'
            elif type == 'zip':
                content_type='application/zip'
                disposition = 'attachment'
            response = HttpResponse(object_file.read(), content_type=content_type)
            response['Content-Disposition'] = f'{disposition}; filename="{file_obj.fname}"'
            
        return response
    else:
        return redirect('signup')

# Add Folder View for Dashboard
def addfolder(request, parent_id):
    if request.user.is_authenticated:
        parent_folder = Folder.objects.get(data_id=parent_id)
        files = File.objects.filter(folder=parent_folder)
        folders=Folder.objects.filter(parent=parent_folder)  
        if request.method == 'POST':
          new_name = request.POST['foldername']   
          if Folder.objects.filter(name=new_name, folderuser=request.user, parent=parent_folder).exists():
                    messages.error(request, "A folder with this name already exists.")
          else:
            folder = Folder.objects.create(name=new_name,folderuser=request.user,parent=parent_folder)
           
            context = {'parent_id':parent_id,'files':files, 'folder':folders, 'parent_name':parent_folder.name}
            print(parent_folder)
            if folder:
             return redirect("folder", parent_id=parent_id)
            else:
                messages.error(request,"Folder Not Created")
                return redirect("folder", parent_id=parent_id)
         
          
        files = File.objects.filter(folder=parent_folder)
        folders=Folder.objects.filter(parent=parent_folder)
        context = {'parent_id':parent_id,'files':files, 'folders':folders, 'parent_name':parent_folder.name}
        return render(request, 'folder.html', context)
    else:
        return redirect('signup')
    


# Go to previous folder feature in Dashboard, the logic behind the working of the "Back" Button
def back(request, parent_name,parent_id):
    old_parent = Folder.objects.get(data_id=parent_id)
    print(old_parent.name)
    if parent_name:  # Check if `parent` is provided
        
        try:
            # Attempt to find the folder with the given name
            parent_folder = Folder.objects.get(data_id=old_parent.data_id)
            
            # Redirect to the folder view with the found parent ID
            if parent_folder.name == 'Home':
                return redirect("folder", parent_id=parent_folder.data_id)
            else:
                super_parent = parent_folder.parent
                return redirect("folder", parent_id = super_parent.data_id)
        except Folder.DoesNotExist:
            # If the folder doesn't exist, redirect to index
            return redirect("index", parent_id=old_parent.data_id)
    else:
        # If no parent is provided, redirect to the index
        return redirect("index", parent_id=old_parent.data_id)
    

#renaming of the objects in Dashboard
def rename(request, parent_id, ):
    parent = Folder.objects.get(data_id=parent_id)
    referer = request.META.get('HTTP_REFERER', '')
  
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        item_type = request.POST.get('item_type')
        new_name = request.POST.get('new_name', '').strip()
       
        if new_name:
            if item_type == 'folder':
                folder = get_object_or_404(Folder, data_id=item_id)
            # Check if a folder with the new name already exists to avoid duplicates
                if Folder.objects.filter(name=new_name, folderuser=folder.folderuser).exists():
                    messages.error(request, "A folder with this name already exists.")
                else:
                   print(folder.name)
                   folder.name = new_name
                   folder.save()
                   messages.success(request, "Folder renamed successfully.")
                   return redirect('folder', parent_id=parent.data_id)  
            else :
                files = File.objects.get(data_id= item_id)
               # Check if a folder with the new name already exists to avoid duplicates
                if File.objects.filter(fname=new_name, folder=parent).exists():
                    messages.error(request, "A file with this name already exists.")
                else:
                   ext = get_file_extension(request,files.fname)
                   new_name = new_name + '.'+ext
                   files.fname = new_name
                   files.save()
                   messages.success(request, "File renamed successfully.")
                   return redirect('folder', parent_id=parent.data_id)           
        else:
            messages.error(request, "Invalid folder type")   
    return redirect('folder', parent_id=parent.data_id) 


    


    

def path_list(parent_id):
    list =""
    try:
        parent = Folder.objects.get(data_id=parent_id)
    except:
        parent = File.objects.get(data_id=parent_id)
    finally:
        list = "None"
    if list != "None":
        while parent.name != 'Home':
           list = list + '/'+ parent.name
           parent = parent.parent
           return list
    else:
        return list


############################################# Moving objects from one path to another for Dashboard and TrashBox(JunkBox) ##########################################################


####################################   Moveing  a object#########################
def path_change(request, parent_id=None):

    if request.user.is_authenticated:
        if request.method == 'POST':
            #new_parent_id = request.POST.get('target_folder')
            object_id = request.POST.get('object_id')
            #new_parent_id = Folder.objects.get(name=new_parent_name)
            new_parent= Folder.objects.get(data_id=parent_id)
            if str(object_id) == str(new_parent.data_id):
                messages.warning(request, f" folder can not be it's own parent!")
                return redirect('folder', parent_id=parent_id)
            try:
                folder = get_object_or_404(Folder, data_id=object_id)
                
                if Folder.objects.filter(name=folder.name, folderuser=request.user).exists():
                    
                    if Folder.objects.filter(name=folder.name, parent=new_parent).exists():
                        folder.name = "copy_"+ folder.name
                        folder.save()
                        messages.success(request, f" {folder.name} is moved with added Name copy {folder.name} to {new_parent.name}")
                    
                    folder.parent = new_parent
                    folder.save()
                    messages.success(request, f" {folder.name} is moved to {new_parent.name}")

                    if Trasher.objects.filter(t_id=folder.data_id).exists():
                            print("found trash")
                            trash = Trasher.objects.get(t_id=object_id)
                            trash.delete()
                    

                    return redirect('folder', parent_id=new_parent.data_id)
                else:
                    messages.error(request, "Invalid folder type") 
            except:
                file = get_object_or_404(File, data_id = object_id)
                if File.objects.filter(fname=file.fname, folder=file.folder).exists():
                    if  File.objects.filter(fname=file.fname, folder=new_parent).exists():
                        file.fname = "copy "+file.fname
                        file.save()
                    file.folder=new_parent
                    file.save()
                    messages.success(request, f" {file.fname} is moved to {new_parent.name}")

                    if Trasher.objects.filter(t_id=object_id).exists():
                            print("found trash")
                            trash = Trasher.objects.get(t_id=file.data_id)
                            trash.delete()
                    return redirect('folder', parent_id=new_parent.data_id)
                else:  
                  messages.error(request, "or invalid name")
        else:
            print("hello1")
            print(parent_id)
            parent = Folder.objects.get(folderuser=request.user, data_id=parent_id)
            folders = Folder.objects.filter(parent=parent)
            files = File.objects.filter(folder=parent)
            context = {'parent_id':parent_id,'files':files, 'folder':folders, 'parent_name':parent.name}
            return render(request,'move.html', context)
        
        
    else:
        print("you are not loged in , log in please")
        return redirect('index' )
    


###################path change with parent with parent name for back option####################

def path_change_back(request,parent_name):
        if parent_name:
            try:
               parent_folder = Folder.objects.get(name=parent_name, folderuser= request.user)
               if parent_folder.name == 'Home':
                  return redirect("path_change", parent_id=parent_folder.data_id)
               else:
                  super_parent = parent_folder.parent
                  return redirect("path_change", parent_id = super_parent.data_id)
            except Folder.DoesNotExist:
            # If the folder doesn't exist, redirect to index
                return redirect("path_change", parent_id=parent_folder.data_id)
        else:
            pass





############################################################### This portion is specfically for TrashBox related view and operatons ##############################################################################

#### for Trash box ### view code #############

def trash_move(request):
    home = Folder.objects.get(name='Home', folderuser=request.user)
    path_change(request,home.data_id)  


################ ################   Deleting a object ###################################

def traching_object(request):
    if request.user.is_authenticated:
       
        trash = Folder.objects.get(name='Trash', folderuser=request.user)
        if request.method == 'POST':
            object_id = request.POST.get('object_id')
            try:
                folder = Folder.objects.get(data_id=object_id, folderuser=request.user)
                parent = Folder.objects.get(data_id=folder.parent.data_id,folderuser=request.user)
                
                if Folder.objects.filter(name=folder.name,data_id=object_id).exists():  
                    Trasher.objects.create(name=folder.name,data_type='folder',t_id=folder.data_id,dlt_by=request.user,prt_id=folder.parent.data_id,path_list=path_list(folder.parent.data_id))
                    folder.parent = trash
                    folder.is_deleted = 'Yes'
                    folder.save()
                    messages.success(request, f"{folder.name} is deleted successfully.You can find it on Trash Box.")
                    return redirect('folder', parent_id=parent.data_id)
                else:
                    messages.error(request, "Invalid folder type") 
                    return redirect('folder', parent_id=parent.data_id)
            except:
                file = get_object_or_404(File, data_id = object_id)
                parent= Folder.objects.get(data_id=file.folder.data_id,folderuser=request.user)
                if File.objects.filter(fname=file.fname, folder=file.folder).exists():
                    data = Trasher.objects.create(name=file.fname, data_type='file', t_id=file.data_id, dlt_by=request.user,prt_id=file.folder.data_id,path_list=path_list(file.folder.data_id))
                    file.folder = trash
                    file.is_deleted = 'Yes'

                    file.save()
                    messages.success(request, f"{file.fname} is deleted successfully.You can find it on Trash Box.")
                    return redirect('folder', parent_id=parent.data_id)
                    
                else:  
                  messages.error(request, "Invalid folder type")
                  return redirect('folder', parent_id=parent.data_id)
        else: 
           messages.error(request, "This is not the right way of traching")
    else: 
           return redirect('Login')

######################  Trash display for trash.html ###########################

def trash_display_with_move(request,obj_id=None):
    if request.user.is_authenticated:
        if request.user.is_authenticated:
            parent = Folder.objects.get(name='Trash', folderuser=request.user)
            trash = Trasher.objects.filter(dlt_by=request.user)
            home = Folder.objects.get(name='Home', folderuser=request.user)
            files = File.objects.filter(folder=home)
            folders = Folder.objects.filter(parent=home, folderuser=request.user)

            if obj_id:
                folder = Folder.objects.get(data_id=obj_id, folderuser=request.user)
                # Call exclude properly or remove if not needed
                folders = Folder.objects.filter(parent=folder, folderuser=request.user).exclude()

                context = {
                    'parent_id': folder.data_id,
                    'folders': folders,
                    'parent': folder,
                    'parent_name': folder.name,
                    'home': home
                }
                return render(request, 'movenew.html', context)

            context = {
                'trash': trash,
                'parent': parent,
                'parent_id': home.data_id,
                'files': files,
                'folders': folders,
                'parent_name': 'Home'
            }
            return render(request, 'trash.html', context)

        else:
            return redirect('Login')

    else: 
           return redirect('Login')
############################### Restoreing a Object from the Trash ####################################
def restore(request,id):
    if request.user.is_authenticated:
        
        if request.method == 'GET':
            print(id , 'this is inside of restore') 
            trash_home= Folder.objects.get(name='Trash', folderuser=request.user)
            try:
                folder =  Folder.objects.get(data_id=id,parent=trash_home)
                print(folder.data_id, trash_home.data_id)
                trash =  Trasher.objects.get(name=folder.name,t_id=folder.data_id)
                if Folder.objects.filter(name=folder.name,data_id=trash.t_id).exists():
                      parent = Folder.objects.get(data_id=trash.prt_id,folderuser=request.user)
                      folder.parent = parent
                      folder.is_deleted = 'No'
                      folder.save()
                      trash.delete()
                      messages.success(request, f" {folder.name} is restored successfully")
                      return redirect('folder', parent_id=parent.data_id)   
                else:
                    messages.error(request, f" {folder.name} is not restored.")
                    return redirect('trash_display_with_move') 
            except:
                file = get_object_or_404(File, data_id = id, folder=trash_home)
                trash =  Trasher.objects.get(name=file.fname,t_id=file.data_id)
                print(trash)
                if File.objects.filter(fname=trash.name,data_id=trash.t_id).exists():
                      parent = Folder.objects.get(data_id=trash.prt_id,folderuser=request.user)
                      file.folder = parent
                      file.is_deleted = 'No'
                      file.save()
                      trash.delete()
                      messages.success(request, f" {file.fname} is restored successfully")
                      return redirect('folder', parent_id=parent.data_id)   
                else:  
                    messages.error(request, f" {file.fname} is not restored.")
                    return redirect('trash_display_with_move') 
                  
        else:
           return redirect('trash_display_with_move')
    else: 
           return redirect('Login')



#################################### Deleteing a object Trash ##########################
def delete_trash(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            id = request.POST.get('object_id')
            try:
                folder = get_object_or_404(Folder, data_id=id,folderuser=request.user)
                if Folder.objects.filter(name=folder.name,data_id=id).exists():
                    if Trasher.objects.filter(name=folder.name,t_id=folder.data_id).exists():
                      trash =  Trasher.objects.get(name=folder.name,t_id=folder.data_id)
                      trash.delete()
                      folder.delete()
                      messages.success(request, f" {folder.name} deleted successfully") 
                      return redirect('trash_display_with_move')
                    
                else:
                    messages.error(request, "Invalid Object(folder) type") 
                    return redirect('trash_display_with_move')
            except:
                file = get_object_or_404(File, data_id = id)
                if File.objects.filter(fname=file.fname, data_id=file.data_id).exists():
                   if Trasher.objects.filter(name=file.fname,t_id=file.data_id).exists():
                      trash =  Trasher.objects.get(name=file.fname,t_id=file.data_id)
                      trash.delete()
                      file.delete()
                      messages.success(request, f" {file.fname} deleted successfully") 
                      return redirect('trash_display_with_move')
                else:  
                  messages.error(request, "Invalid Object(file) type")
                  return redirect('trash_display_with_move')
        else:
           return redirect('trash_display_with_move')
    else: 
           return redirect('login')
    

########################################################################  For Share Module #####################################################################################
    
#sharing a objects feature view logic
def Share_objects(request, parent_id):
    if not request.user.is_authenticated:
        return redirect('signup')

    # Fetch POST data
    object_id = request.POST.get('object_id')
    permission = request.POST.get('PermissionSelect')
    user_id = request.POST.get('user_id')
    print(user_id , "this is user id")
    # Get the user object

    user = ""

    # Try to share a folder first
    try:
        folder = Folder.objects.get(data_id=object_id)
        if user_id:
           user = get_object_or_404(User, id=user_id)
        # Use update_or_create to update existing permission or create new one
        
           folder.shared_with_folder.add(user)
           UserFolderPermission.objects.update_or_create(
            user=user, folder=folder,
            defaults={'permission': permission}
            )
           remove_users = request.POST.getlist("remove_users[]")
           Stop_sharing(request, object_id, remove_users)
           messages.success(request, f" {folder.name} is shared to @{user} and {remove_users} are remove from the share  list!")

           return redirect('folder', parent_id=parent_id)
        remove_users = request.POST.getlist("remove_users[]")
        Stop_sharing(request, object_id, remove_users)
        messages.success(request, f" user or users are remove from the share  list!")

           

    except Folder.DoesNotExist:
        pass  # If Folder does not exist, move on to File logic

    # Now, try to share a file
    try:
        file = File.objects.get(data_id=object_id)
        if user_id:
            user = get_object_or_404(User, id=user_id)
        # Use update_or_create to update existing permission or create new one
            file.shared_with_file.add(user)
            check = UserFilePermission.objects.update_or_create(
            user=user, file=file,
            defaults={'permission': permission}
        )   
            remove_users = request.POST.getlist("remove_users[]")
            Stop_sharing(request, object_id, remove_users)
            messages.success(request, f" {file.fname} is shared to @{user} and {remove_users} are remove from the share  list!")
            return redirect('folder', parent_id=parent_id)
       
        remove_users = request.POST.getlist("remove_users[]")
        Stop_sharing(request, object_id, remove_users)
        messages.success(request, f"user or users are remove from the share list!")
    except File.DoesNotExist:
        # Handle file not found error if needed
        pass

    # If neither folder nor file is found, you can redirect with an error message or log it
    return redirect('folder', parent_id=parent_id)





# To display the shared users for a object in the shareFrom like how many users are in the list of shared list for that object with permission
def load_permitted_users(request, object_id):
    # Initialize the shared_users variable
    shared_users = []
    
    try:

        shared_object = get_object_or_404(Folder, data_id=object_id)
        shared_users = UserFolderPermission.objects.filter(folder=shared_object).select_related("user")

    except:
         shared_object = get_object_or_404(File, data_id=object_id)
         shared_users = UserFilePermission.objects.filter(file=shared_object).select_related("user")
    data = {
        "shared_users": [
            {
                "id": share.user.id,
                "username": share.user.username,
                "permission": share.get_permission_display(),
            }
            for share in shared_users
        ]
    }
    return JsonResponse(data)

## stop sharing objects
def Stop_sharing(request, object_id, remove_users):
    try:
        folder = get_object_or_404(Folder, data_id=object_id)
        
        print(remove_users, " this is remove users")
        for user_id in remove_users:
             # Retrieve the user instance or you can directly filter using user_id
                print(user_id)
                
                user = User.objects.get(id=user_id)
                  # Fetch user instance using the user ID
                UserFolderPermission.objects.filter(user=user, folder=folder).delete()
                folder.shared_with_folder.remove(user) 
                print(" sharing_foldere ")      
                
    except:
        file = File.objects.get(data_id=object_id)
        print(" sharing_file ")
        for user_id in remove_users:
             # Retrieve the user instance or you can directly filter using user_id
                
                user = User.objects.get(id=user_id)
                  # Fetch user instance using the user ID
                UserFilePermission.objects.filter(user=user, file=file).delete()
                file.shared_with_file.remove(user) 

########################################################### For the Copy Module ############################################################################################################

    
#copy and paste feature logic
def item_coping(request,parent_id):
    if request.user.is_authenticated:
       
        if request.method == 'POST':
            #new_parent_id = request.POST.get('target_folder')
            
           
            object_id = request.POST.get('object_id')
            new_parent= Folder.objects.get(data_id=parent_id)

            try:
                folder = get_object_or_404(Folder, data_id=object_id)
                if Folder.objects.filter(name=folder.name, folderuser=request.user).exists():
                    
                    if str(object_id) == str(new_parent.data_id):
                         messages.warning(request, f" folder can not be it's own parent!")
                         return redirect('folder', parent_id=parent_id)
                    elif Folder.objects.filter(name=folder.name, parent=new_parent).exists():
                       folderadd = Folder.objects.create(name='copy ' + folder.name,folderuser=request.user,parent=new_parent)
                    
                    else:
                        folderadd = Folder.objects.create(name=folder.name,folderuser=request.user,parent=new_parent)
                        messages.success(request, f" {folder.name} is copied to {new_parent.name} successfully.")
                    filelist = File.objects.filter(folder=folder)
                    for files in filelist:
                        file_coping(request,files,folderadd)
                    for folders in folder.subfolders.all():
                        status = folder_coping(request,folders,folderadd)
                    return redirect('folder', parent_id=new_parent.data_id)
                else:
                    messages.error(request, "Invalid folder type") 
            except:
                file = get_object_or_404(File, data_id = object_id)
                file_coping(request,file,new_parent)
                messages.success(request, f" {file.fname} is copied to {new_parent.name} successfully.")
                return redirect('folder', parent_id=new_parent.data_id)      
        else:
           print("hello")
           print(parent_id)
           parent = Folder.objects.get(folderuser=request.user, data_id=parent_id)
           folders = Folder.objects.filter(parent=parent)
           files = File.objects.filter(folder=parent)
           context = {'parent_id':parent_id,'files':files, 'folder':folders, 'parent_name':parent.name}
           return render(request,'copy.html', context)   
    else:
        print("you are not loged in , log in please")
        return redirect('index' )
    
# View for item_coping function file copy feature enable
def file_coping(request,file,new_parent):
    if File.objects.filter(fname=file.fname, folder=file.folder).exists():
        if  File.objects.filter(fname=file.fname, folder=new_parent).exists():
            fileadd = File.objects.create(fname='copy ' + file.fname,folder=new_parent,file=file.file)
            
        elif not  File.objects.filter(fname=file.fname, folder=new_parent).exists():
            fileadd = File.objects.create(fname=file.fname,folder=new_parent,file=file.file)     
                       
        else:  
            messages.error(request, "or invalid name")        

# view for item_coping function for enabling the folder_coping
def folder_coping(request,folder,new_parent):
  
    folderadd = Folder.objects.create(name=folder.name,folderuser=request.user,parent=new_parent)
    folderlist = folder.subfolders.all()
    if folderlist == None:
        return "done"
    filelist = File.objects.filter(folder=folder)
    for files in filelist:
        file_coping(request,files,folderadd)
    for folders in folder.subfolders.all():
        folder_coping(request,folders,folderadd)


################################################################ For the Folder Download Module #######################################################################################


#####Download folders in the Dashboared and ShareBox##########

def download_folder(request, folder_id):
    folder = get_object_or_404(Folder, data_id=folder_id)  # Corrected to use id

    # Create a zip file in memory
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add files from the main folder to the zip
        filelist = File.objects.filter(folder=folder)
        for file_obj in filelist:
            # Use the file's path to add the actual file to the zip
            file_path = file_obj.file.path
            zip_file.write(file_path, arcname=file_obj.fname)  # fname is used as the filename in the zip

        # If folder has subfolders, add their files recursively
        def add_folder_to_zip(subfolder, parent_path):
            filelist = File.objects.filter(folder=subfolder)
            for subfile in filelist:
                # Set the path of the file inside the zip with the correct folder structure
                file_path = os.path.normpath(subfile.file.path)
                arcname = os.path.join(parent_path, subfile.fname)  # Create a relative path in the zip
                zip_file.write(file_path, arcname=arcname)

            # Recurse into subfolders
            for subsubfolder in subfolder.subfolders.all():  # Assumes related_name='subfolders' is used in the model
                add_folder_to_zip(subsubfolder, os.path.join(parent_path, subsubfolder.name))

        # Start adding subfolders (if any)
        for subfolder in folder.subfolders.all():  # Fixed typo: subforders -> subfolders
            add_folder_to_zip(subfolder, subfolder.name)

    # Set the buffer position to the beginning
    zip_buffer.seek(0)

    # Return the zip file as a downloadable response
    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename={folder.name}.zip'
    return response
    

 #################################################################   Authentication module ################################################################################################

# Password change by the users
def Change_password(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            new_passwd = request.POST['New_password']
            confirm_passwd = request.POST['confirm_password']
            user = User.objects.get(username=request.user.username)
            if confirm_passwd == new_passwd:
                user.set_password(new_passwd)  # Properly hash the password
                user.save()  # Save the user with the new password
                messages.success(request, "Password updated successfully!")
                return redirect('login')  # Redirect to the desired page
         
            else:
                messages.warning(request, "New and confirm password do not match")
                return redirect('Change_password')  
    return redirect('signup')    


# View For SignUp the user
def SignUp(request): 
    if request.user.is_authenticated:
        
        return redirect('index')
    else:
        if request.method == 'POST':
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']
            cpassword = request.POST['cpassword']
            firstname = request.POST['fname']
            lname = request.POST['lname']
            if username and password and email and cpassword and firstname and lname:
                if User.objects.filter(username__iexact=username).exists():
                    messages.warning(request,"User already exists, chose another name")
                    return redirect('signup')
                if password == cpassword:
                    user = User.objects.create_user(username,email,password)
                    user.first_name = firstname
                    user.last_name = lname
                    user.save()
                    if user:
                        messages.success(request,"User Account Created")
                        return redirect("login")
                    else:
                        messages.error(request,"User Account Not Created")
                else:
                    messages.error(request,"Password Not Matched")
                    redirect("signup")
        return render(request,'signup.html')
    
    
# View For Log in the user
def Login(request):
    if request.user.is_authenticated:
    
        return redirect('index')
    else:
        user = ''
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            if username and password:
                if not authenticate(username=username,password=password):
                    messages.warning(request,"Invaild username or password")
                    return redirect('login')
                else:
                    user = authenticate(username=username,password=password)
                if user is not None:
                    login(request,user)
                    if not Folder.objects.filter(folderuser=request.user,name='Home'):
                        folder = Folder.objects.create(name='Home',folderuser=request.user,parent=None)
                    folder = Folder.objects.get(folderuser=request.user,name='Home')
                    if not Folder.objects.filter(folderuser=request.user,name='Trash'):
                        folder1 = Folder.objects.create(name='Trash',folderuser=request.user,parent=None)
                    return redirect('index_with_parent',parent_id=folder.data_id)
        return render(request,'login.html')
    

# User logout function
def Logout(request):
    home = Folder.objects.get(folderuser=request.user,name='Home')
    logout(request)
    return redirect("index")




##### ##################################################################  This section is for the Share Function to work on #####################################################################################
#Cover(ing the Sharing portion view

#Cover(ing the Sharing portion view
def display_sharing(request, tab=None):
    files_by_you = File.objects.filter(Q(shared_with_file__isnull=False,folder__folderuser =request.user))
    folders_by_you = Folder.objects.filter(shared_with_folder__isnull=False,folderuser =request.user)

    files_with_you = File.objects.filter(shared_with_file =request.user)
    folders_with_you = Folder.objects.filter(shared_with_folder=request.user)
    context = {'files_by': files_by_you, 'folders_by':folders_by_you, 'files_with': files_with_you, 'folders_with':folders_with_you, 'tab':tab}
    return render(request,'share-index.html',context)
    
    
    
# Shows the content of a folder and handles the files upload in ShareBox
def inside_sharing_fupload(request,parent_id, user_permissions=None,parent_name=None):

    if request.user.is_authenticated:
        parent_folder = Folder.objects.get(data_id=parent_id) 
        files = File.objects.filter(folder=parent_folder)
        folders=Folder.objects.filter(parent=parent_folder)
        user_list = User.objects.exclude(id=request.user.id)
        if request.method == 'POST':
            filelist = request.FILES.getlist('file')
            for file in filelist:
               name=(str(file))
               if not File.objects.filter(fname=name,folder=parent_folder,file=file).exists():        
                  fileadd = File.objects.create(fname=name,folder=parent_folder,file=file)
               else:
                 messages.warning(request, f"File {(str(file))} already exists and was not uploaded.")
        if not user_permissions:
            user_permissions = UserFolderPermission.objects.filter(folder=parent_folder, user=request.user)
            for permission in user_permissions:               
                   user_permissions =  permission.get_permission_display()
        if not parent_name:
            parent_name = parent_folder.name
            print(parent_name)
        context = {'parent_id':parent_id,'files':files, 'folder':folders, 'parent_name':parent_name, 'users': user_list,'user_permissions': user_permissions,}
        return render(request,'share-working.html',context)       
    
    else:
        return redirect('signup')


# Add Folder View from ShareBox
def addfolder_sharing(request, parent_id,permissions,parent_name):
    if request.user.is_authenticated:
        parent_folder = Folder.objects.get(data_id=parent_id)
        if request.method == 'POST':
          new_name = request.POST['foldername']   
          if Folder.objects.filter(name=new_name, folderuser=request.user, parent=parent_folder).exists():
                    messages.error(request, "A folder with this name already exists.")
          else:
            try:
                folder = Folder.objects.create(name=new_name,folderuser=parent_folder.folderuser,parent=parent_folder)
            except:
                messages.error(request,"Folder Not Created")  
            
            if folder:
             return redirect("inside_sharing_fupload", parent_id=parent_id,user_permissions=permissions,parent_name=parent_name)
            else:
                messages.error(request,"Folder Not Created")
                return redirect("inside_sharing_fupload", parent_id=parent_id,user_permissions=permissions,parent_name=parent_name) 
    else:
        return redirect("index",parent_id= parent_id )
    
#renaming of the objects  from shareBox
def rename_sharing(request, parent_id, permissions,parent_name):
    if request.user.is_authenticated:
        parent = Folder.objects.get(data_id=parent_id)
        if request.method == 'POST':
            item_id = request.POST.get('item_id')
            item_type = request.POST.get('item_type')
            new_name = request.POST.get('new_name', '').strip()
            if new_name:
                # for folder rename
                if item_type == 'folder':
                    folder = get_object_or_404(Folder, data_id=item_id)
                    # Check if a folder with the new name already exists to avoid duplicates
                    if Folder.objects.filter(name=new_name, folderuser=folder.folderuser).exists():
                        messages.error(request, "A folder with this name already exists.")
                    else:
                        print(folder.name)
                        folder.name = new_name
                        folder.save()
                        messages.success(request, "Folder renamed successfully.")
                        return redirect("inside_sharing_fupload", parent_id=parent_id,user_permissions=permissions,parent_name=parent_name)
                # for file rename
                else :
                    files = File.objects.get(data_id= item_id)
                    # Check if a folder with the new name already exists to avoid duplicates
                    if File.objects.filter(fname=new_name, folder=parent).exists():
                        messages.error(request, "A file with this name already exists.")
                    else:
                        ext = get_file_extension(request,files.fname)
                        new_name = new_name + '.'+ext
                        files.fname = new_name
                        files.save()
                        messages.success(request, "File renamed successfully.")
                        return redirect("inside_sharing_fupload", parent_id=parent_id,user_permissions=permissions,parent_name=parent_name)
       
        else:
            messages.error(request, "Invalid folder type")
    return redirect('signup') 

# Loding parent based on the request from the path plate shown in the shareBox 
def load_parent_sharing(request, parent_id, super_parent, permissions):
    if request.user.is_authenticated:
        
        try:
            old_parent = Folder.objects.get(data_id=parent_id)
            print(old_parent.folderuser, super_parent)
        except Folder.DoesNotExist:
            # Folder with parent_name does not exist
            messages.error(request, "Folder not found.")
        if request.user == old_parent.folderuser:
             return redirect("inside_sharing_fupload", parent_id=old_parent.data_id, parent_name=super_parent,user_permissions=permissions)


        while old_parent and old_parent.name != "Home":
            print(old_parent.shared_with_folder , 'hello')
            # Check if the folder is shared with the user
            if request.user in old_parent.shared_with_folder.all():
                
                try:
                    # Retrieve the folder to redirect to
                    parent = Folder.objects.get(data_id=parent_id)
                    # Redirect to the folder view, passing user_permissions
                    return redirect("inside_sharing_fupload", parent_id=parent.data_id,  parent_name=super_parent,user_permissions=permissions)
                except Folder.DoesNotExist:
                    # Handle the case where the folder doesn't exist
                    messages.error(request, "Target folder not found.")
                    return redirect("inside_sharing_fupload", parent_id=old_parent.data_id,parent_name=super_parent,user_permissions=permissions)
            
            # Move up the folder hierarchy
            old_parent = old_parent.parent
        
        # If loop completes without finding a match, handle it
        messages.error(request, "You do not have access to this folder.")
        return redirect("inside_sharing_fupload", parent_id=old_parent.data_id,parent_name=super_parent,user_permissions=permissions)
    # Redirect to signup if the user is not authenticated
    else:
        return redirect('signup')

    
    


