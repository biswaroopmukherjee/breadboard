import datetime

from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField, ArrayField
from django.utils import timezone

from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


"""
Defaults for foreign keys. Dummies are necessary because the true run objects
will be created simultaneously with the images
"""
DEFAULT_RUN = 1
DEFAULT_LAB = 1
DEFAULT_DATASET = 1
DEFAULT_PROJECT = 1
def default_params(): return {}


class UserProfile(models.Model):
    """
    A class for extending the django user model to include more information
    like the lab in which the user works, and maybe more stuff
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    lab = models.ForeignKey('Lab', on_delete=models.SET_NULL, blank=True, null=True, related_name='userprofiles')
    description = models.CharField('A short user description', max_length=300,blank=True, null=True )


    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'userprofile'
        verbose_name_plural =  'userprofiles'




class Image(models.Model):
    """
    Class for images taken in the experiment.
    """
    name = models.CharField(max_length=200)
    created = models.DateTimeField('time created', default=timezone.now, blank=True)
    notes = models.TextField('image notes', blank=True, null=True)
    filepath = models.TextField('filepath location for raw data on / in the MIT server', blank=True, null=True)
    tags = JSONField('tags for the image', default=default_params, blank=True, null=True)
    thumbnail = models.TextField('filepath for an image thumbnail', blank=True, null=True)
    total_atoms = models.FloatField('number of atoms in the image. Can be either from fitting or from pixel summing', blank=True, null=True)
    odpath = models.TextField('filepath location for the od fits file on / in the MIT server', blank=True, null=True)
    atomsperpixel = models.TextField('filepath location for the atoms per pixel on / in the MIT server', blank=True, null=True)
    cropi = JSONField('cropi for the image', default=default_params, blank=True, null=True)
    settings = JSONField('additional settings, such as Isat, fudge, subsample, etc', default=default_params, blank=True, null=True)
    pixel_size = models.FloatField(default=1, blank=True, null=True)
    # Choices for atoms in the image. Can be used for processing, and integration with camera UIs
    LITHIUM = 'Li'
    SODIUM = 'Na'
    POTASSIUM = 'K'
    ATOM_CHOICES = (
        (LITHIUM, 'Lithium'),
        (SODIUM, 'Sodium'),
        (POTASSIUM, 'Potassium')
    )
    atom = models.CharField(
        'atom used in the imaging: eg Li, Na, K, etc ',
        max_length=2,
        choices=ATOM_CHOICES,
        default=LITHIUM,
    )

    # relationships
    run = models.ForeignKey('Run', on_delete=models.PROTECT, blank=True, null=True, related_name='images')
    lab = models.ForeignKey('Lab', on_delete=models.PROTECT, related_name='images', null=True, blank=True)

    class Meta:
        ordering = ['-created', 'name']
        verbose_name = 'image'
        verbose_name_plural =  'images'

    def __str__(self):
        return self.name





class Run(models.Model):
    """
    Class for experimental runs.
    Each cicero cycle should generate a new run object
    """
    created = models.DateTimeField('datetime object created. Could be different by a few sec from runtime', default=timezone.now , blank=True)
    runtime = models.DateTimeField('datetime for expt run', default=timezone.now , blank=True)
    workday = models.DateField('date of lab work. (often overflows through midnight)', default = datetime.date.today, blank=True )
    parameters = JSONField('Variables and parameters', default=default_params, blank=True, null=True)
    bad_shot = models.BooleanField('Was this run a bad shot?', default=False, blank=True)
    notes = models.TextField('Run notes', default='', blank=True, null=True)

    # Relationships
    lab = models.ForeignKey('Lab', on_delete=models.PROTECT, related_name='runs', null=True, blank=True)
    dataset = models.ForeignKey('Dataset', on_delete=models.SET_NULL, null=True, related_name='runs', blank=True)

    class Meta:
        ordering = ['-runtime']
        verbose_name = 'run'
        verbose_name_plural =  'runs'

    def __str__(self):
        return self.runtime.strftime("%Y-%m-%d %H:%M:%S")



class Dataset(models.Model):
    """
    Class for a dataset: a collection of runs
    """
    name = models.CharField('Dataset name', max_length=200, default='Dataset 1')
    created = models.DateTimeField('datetime created', default=timezone.now, blank=True)
    notes = models.TextField('Dataset notes', default='', blank=True, null=True)
    flag = models.CharField('Dataset flags', max_length=200, default='', blank=True, null=True)
    tags =  JSONField('tags for the dataset', default=default_params, blank=True, null=True)

    # Relationships
    project = models.ForeignKey('Project', on_delete=models.SET_NULL,  blank=True, null=True, related_name='datasets')
    lab = models.ForeignKey('Lab', on_delete=models.SET_NULL,  blank=True, null=True, related_name='datasets')

    class Meta:
        ordering = ['name']
        verbose_name = 'dataset'
        verbose_name_plural =  'datasets'

    def __str__(self):
        return self.name




class Project(models.Model):
    """
    Class for a project: a collection of datasets
    """
    name = models.CharField('project name', max_length=200, default='Project1')
    created = models.DateTimeField('datetime created', default=timezone.now, blank=True)
    notes = models.TextField('project notes', default='', blank=True, null=True)

    # relationships:
    lab = models.ForeignKey('Lab', on_delete=models.SET_NULL, blank=True, null=True, related_name='projects')

    class Meta:
        ordering = ['name']
        verbose_name = 'project'
        verbose_name_plural =  'project'

    def __str__(self):
        return self.name



class Lab(models.Model):
    """
    Class for a group of users that work in a Lab. Stores lab relevant info
    """
    name = models.CharField(max_length=20, default='bec1')
    created = models.DateTimeField('date lab was registered', default=timezone.now, blank=True)
    info = models.TextField('detailed info about the lab', blank=True, null=True)
    photo = models.TextField('filepath to the lab photo', blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'lab'
        verbose_name_plural =  'labs'

    def __str__(self):
        return self.name
