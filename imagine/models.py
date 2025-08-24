from datetime import timezone
import uuid
from django.db import models
from django.contrib.auth.models import User

# Permission choices
PERMISSION_CHOICES = (
    ('read', 'Read'),
    ('write', 'Write'),
    ('owner', 'Owner'),
)
################### For Folder ###############################################################################################

#Folder object's model entity creatation.
class Folder(models.Model):
    data_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    folderuser = models.ForeignKey(User,on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subfolders')
    data_type = models.CharField(max_length=20, default='folder', choices=[('folder', 'Folder'), ('file', 'File')])
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True) 
    updated_at = models.DateTimeField(auto_now=True, blank=True)
    is_deleted = models.CharField(max_length=20, default='No', choices=[('Yes', 'yes'), ('No', 'no')])
    shared_with_folder = models.ManyToManyField(User, through='UserFolderPermission', related_name='shared_folders', blank=True)


    def get_full_path(self, max_depth=10, current_depth=0):
        # Stop recursion if max depth is reached
        if current_depth >= max_depth:
            return "..."

        # Recursively build the full path
        if self.parent:
            return f"{self.parent.get_full_path(max_depth, current_depth + 1)}/{self.name}"
        return self.name
    
    def __str__(self):
        return self.name
    
##  sharing permission setter with the users whom are added ih the shared users list for Folder ShareBox Display   
class UserFolderPermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)
    permission = models.CharField(max_length=10, choices=PERMISSION_CHOICES)
    shared_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'folder')  # Ensure each user has a unique permission per file

    def __str__(self):
        return f"{self.user.username} has {self.get_permission_display()} permission for {self.folder.name}"
    
## ##################################    For Files ###########################################################################################################################

## File  object's model entity creation  
class File(models.Model):
    data_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fname = models.CharField(max_length=50)
    folder = models.ForeignKey(Folder,on_delete=models.CASCADE)
    file = models.FileField(upload_to="Files")
    data_type = models.CharField(max_length=20, default='file', choices=[('folder', 'Folder'), ('file', 'File')])
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)   
    updated_at = models.DateTimeField(auto_now=True, blank=True)
    is_deleted = models.CharField(max_length=20, default='No', choices=[('Yes', 'yes'), ('No', 'no')])    
    shared_with_file = models.ManyToManyField(User, through='UserFilePermission',related_name='shared_files', blank=True)

    def __str__(self):
        return self.fname
    

##  sharing permission setter with the users whom are added ih the shared users list for the File Sharebox Display 
   
class UserFilePermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    permission = models.CharField(max_length=10, choices=PERMISSION_CHOICES)
    shared_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'file')  # Ensure each user has a unique permission per file

    def __str__(self):
        return f"{self.user.username} has {self.get_permission_display()} permission for {self.file.fname}"


#### Junk Box #################################################################################################################    
class Trasher(models.Model):
    t_id = models.UUIDField(primary_key=True, editable=False, unique=True)
    name = models.CharField(max_length=50)
    data_type = models.CharField(max_length=20, default='folder', choices=[('folder', 'Folder'), ('file', 'File')])
    dlt_by = models.ForeignKey(User,on_delete=models.CASCADE)
    dlt_at = models.DateTimeField(auto_now=True, blank=True)
    prt_id = models.UUIDField(editable=False, unique=False)
    path_list = models.CharField(max_length=250,default=None)
    
    def __str__(self):
        return str(self.t_id)