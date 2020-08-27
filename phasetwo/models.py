from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.contrib.auth.models import User
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import AES, PKCS1_OAEP
from datetime import date
import secrets
import json
import os

from orbit.fields import GenderField

TOKEN_BYTES = 16

def mint_token():
    return secrets.token_urlsafe(TOKEN_BYTES)
def mint_id():
    return secrets.randbelow(1000000)

def encrypt(data):
    '''
    Encrypt data, returning dict of encryption info. As data to encrypt is of an unknown size, strategy is to use AES to encrypt the data, and RSA to encrypt the AES key.
    '''
    # Get keys
    public_key = RSA.import_key(settings.PII_KEY_PUBLIC)
    aes_key = secrets.token_bytes(32) # AES-256, i.e. 256/8=32
    
    # Encrypt the AES 'session' key with the public RSA key
    cipher_rsa = PKCS1_OAEP.new(public_key)
    enc_aes_key = cipher_rsa.encrypt(aes_key)
    
    # Encrypt the data using AES
    cipher_aes = AES.new(aes_key, AES.MODE_EAX)
    ciphertext, mac_tag = cipher_aes.encrypt_and_digest(data)
    
    return {
        'enc_aes_key': enc_aes_key,
        'aes_nonce': cipher_aes.nonce,
        'aes_mac_tag': mac_tag,
        'aes_ciphertext': ciphertext,
    }
    
def decrypt(enc_aes_key, aes_nonce, aes_mac_tag, aes_ciphertext, private_key_pem):
    '''
    Decrypt data, returning bytes.
    '''
    if private_key_pem is None:
        print('Attempting to decrypt without private key')
        return None
        
    private_key = RSA.import_key(private_key_pem)
    
    # Decrypt the AES 'session' key with the private RSA key
    cipher_rsa = PKCS1_OAEP.new(private_key)
    aes_key = cipher_rsa.decrypt(enc_aes_key)
    
    # Decrypt the data with the AES session key
    cipher_aes = AES.new(aes_key, AES.MODE_EAX, aes_nonce)
    data = cipher_aes.decrypt_and_verify(aes_ciphertext, aes_mac_tag)
    
    return data


class EncryptedBlobModel(models.Model):
    '''
    Abstract base class for models that hold an encrypted blob of data
    '''
    class Meta:
        abstract = True
        
    enc_aes_key = models.BinaryField(max_length=16)
    aes_nonce = models.BinaryField(max_length=16)
    aes_mac_tag = models.BinaryField(max_length=16)
    aes_ciphertext = models.BinaryField()
    
    def decrypt(self, private_key_pem = settings.PII_KEY_PRIVATE):
        data = decrypt(
            self.enc_aes_key,
            self.aes_nonce,
            self.aes_mac_tag,
            self.aes_ciphertext,
            private_key_pem
            )
        
        if data is None:
            return None
        
        # Transform back into fields
        obj = json.loads(data.decode("utf-8"))
        
        return obj


class CollectionPeriod(models.Model):
    '''
    A named data collection period.
    '''
    name = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        )
    start = models.DateField(
        )
    end = models.DateField(
        )

    def __str__(self):
        return self.name


class CollectionPeriodDefault(models.Model):
    '''
    A chosen collection period. To be a single record to set the CollectionPeriod for new Participants
    '''
    period = models.ForeignKey(
        CollectionPeriod,
        on_delete = models.PROTECT,
        )


def default_collection_period_pk():
    '''
    Default collection period for a Participant. Creates if missing.
    '''
    try:
        default = CollectionPeriodDefault.objects.get(pk=1)
    except CollectionPeriodDefault.DoesNotExist:
        period = CollectionPeriod.objects.first()
        if period is None:
            period = CollectionPeriod.objects.create(
                name='',
                start=date.today(),
                end=date.today(),
                )
        default = CollectionPeriodDefault.objects.create(
            pk=1,
            period=period
            )
    return default.period.pk


class ParticipantManager(models.Manager):
    def create_participant(self, user, pii_email, pii_name):
        '''
        Create and save a participant record, encrypting the PII fields as a binary blob.
        '''
        # Transform email and name into bytes for encryption
        info = {
            'email': pii_email,
            'name': pii_name,
        }
        data = json.dumps(info).encode('utf-8')
        
        # Encrypt and create
        return self.create(user=user, **encrypt(data))


class Participant(EncryptedBlobModel):
    '''
    A study participant. Generates randomised ID suitable to refer to the participant throughout the research. Email, name are held in encrypted blob.
    The corresponding user is a machine-generated construct to authorise API access. Should be no PII there, just jibberish.
    '''
    id = models.IntegerField(
        primary_key=True,
        default=mint_id,
        )
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        )
    in_study = models.BooleanField(
        default=True,
        )
    survey_started = models.DateTimeField(
        null=True,
        blank=True,
        )
    survey_token = models.CharField(
        default=mint_token,
        max_length=TOKEN_BYTES * 2, # average base64 encoding = 1.3x
        unique=True,
        )
    collection_period = models.ForeignKey(
        CollectionPeriod,
        default=default_collection_period_pk,
        on_delete=models.SET_DEFAULT, 
        )
    objects = ParticipantManager()

    @property
    def survey_done(self):
        return Survey.objects.filter(participant=self).exists()
        
    def __str__(self):
        return f"P{self.id}"

class SurveyManager(models.Manager):
    def create_survey(self, participant, pii_fields):
        '''
        Create and save a survey record, encrypting the supplied fields as a binary blob.
        '''
        # Transform survey data (a dict) into bytes
        data = json.dumps(pii_fields).encode('utf-8')
        
        # Encrypt and create
        return self.create(
            participant=participant,
            **encrypt(data),
            )
        

class Survey(EncryptedBlobModel):
    '''
    The survey data completed by a participant. Held in an encrypted blob.
    '''
    participant = models.OneToOneField(
        Participant,
        on_delete=models.CASCADE,
        )
    
    objects = SurveyManager()
    
    def __str__(self):
        return f"Survey for Participant {self.participant.id}"

class Thing(models.Model):
    '''
    The thing the participant is going to label and capture videos of
    '''
    label_participant = models.CharField(
        max_length=50,
        )
    label_validated = models.CharField(
        max_length=50,
        )
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        )
    created = models.DateField(auto_now_add=True)
    
    @property
    def label(self):
        return self.label_validated if self.label_validated else self.label_participant
    
    @property
    def video_count(self):
        return self.video_set.count()
    
    @property
    def video_breakdown(self):
        counts = []
        for t in Video.TECHNIQUES:
            counts.append(f"{t[0]}:{self.video_set.filter(technique=t[0]).count()}")
        return ' '.join(counts)

    def __str__(self):
        return f"{ self.participant.id }: { self.label } ({ self.video_count } videos)"
    

def random_filename(instance, filename):
    return secrets.token_urlsafe()

class Video(models.Model):
    '''
    The participant-shot video, as file.
    '''
    TECHNIQUES = (
        ('T', 'Train'),
        ('Z', 'Test: Zoom'),
        ('P', 'Test: Pan'),
        )
    VALIDATION = (
        ('-', 'Unvalidated'),
        ('P', 'Reject: video shows PII'),
        ('I', 'Reject: video inappropriate'),
        ('M', 'Reject: video does not feature object'),
        ('C', 'Video is clean'),
        )
    thing = models.ForeignKey(
        Thing,
        on_delete=models.CASCADE,
        )
    file = models.FileField(
        upload_to=random_filename,
        )
    technique = models.CharField(
        max_length=1,
        choices=TECHNIQUES,
        default='N',
        )
    validation = models.CharField(
        max_length=1,
        choices=VALIDATION,
        default='-',
        )
    in_time = models.DecimalField(
        null=True,
        blank=True,
        max_digits=4,
        decimal_places=2,
        )
    out_time = models.DecimalField(
        null=True,
        blank=True,
        max_digits=4,
        decimal_places=2,
        )
    created = models.DateField(auto_now_add=True)
     
    def __str__(self):
        return f"P{self.thing.participant.id}: {self.thing.label}/{self.get_technique_display()}. {self.get_validation_display()}"

@receiver(models.signals.post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    '''
    Deletes file when corresponding `Video` object is deleted.
    '''
    if instance.file:
        try:
            os.remove(instance.file.path)
        except FileNotFoundError:
            # TODO: Logging
            print(f'In Video post_delete, could not delete {instance.file.path}')

@receiver(models.signals.pre_save, sender=Video)
def auto_delete_file_on_change(sender, instance, **kwargs):
    '''
    Deletes old file when corresponding `Video` object is updated with new file.
    '''
    if not instance.pk:
        return False

    try:
        old_file = Video.objects.get(pk=instance.pk).file
    except Video.DoesNotExist:
        return False

    new_file = instance.file
    if not old_file == new_file:
        try:
            os.remove(old_file.path)
        except FileNotFoundError:
            # TODO: Logging
            print(f'In Video pre_save, could not delete {instance.file.path}')
