from django.db import models
from django.conf import settings

from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import AES, PKCS1_OAEP
from datetime import datetime
import secrets
import json

from orbit.fields import GenderField

TOKEN_BYTES = 16

def mint_token():
    return secrets.token_urlsafe(TOKEN_BYTES)
def mint_id():
    return secrets.randbelow(10000)

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
    
def decrypt(enc_aes_key, aes_nonce, aes_mac_tag, aes_ciphertext):
    '''
    Decrypt data, returning bytes.
    '''
    private_key_pem = settings.PII_KEY_PRIVATE
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
    
    def decrypt(self):
        data = decrypt(
            self.enc_aes_key,
            self.aes_nonce,
            self.aes_mac_tag,
            self.aes_ciphertext
            )
        
        if data is None:
            return None
        
        # Transform back into fields
        obj = json.loads(data.decode("utf-8"))
        
        return obj


class ParticipantManager(models.Manager):
    def create_participant(self, email, name):
        '''
        Create and save a participant record, encrypting the supplied fields as a binary blob.
        '''
        # Transform email and name into bytes
        info = {
            'email': email,
            'name': name,
        }
        data = json.dumps(info).encode('utf-8')
        
        # Encrypt and create
        return self.create(**encrypt(data))


class Participant(EncryptedBlobModel):
    '''
    A study participant, with human-usable randomised ID and email, name in encrypted blob.
    '''
    id = models.IntegerField(
        primary_key=True,
        default=mint_id,
        )
    survey_started = models.DateTimeField(
        null=True,
        )
    survey_token = models.CharField(
        default=mint_token,
        max_length=TOKEN_BYTES * 2, # average base64 encoding = 1.3x
        unique=True,
        )
    
    objects = ParticipantManager()
    
    @property
    def survey_done(self):
        return Survey.objects.filter(participant=self).exists()


class SurveyManager(models.Manager):
    def create_survey(self, participant, fields):
        '''
        Create and save a survey record, encrypting the supplied fields as a binary blob.
        '''
        # Transform survey data (a dict) into bytes
        data = json.dumps(fields).encode('utf-8')
        
        # Encrypt and create
        return self.create(
            participant=participant,
            **encrypt(data),
            )
        

class Survey(EncryptedBlobModel):
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        )
    
    objects = SurveyManager()
    
    def __str__(self):
        return f"Survey for Participant {self.participant.id}"


class LabelledMedia(models.Model):
    label = models.CharField(max_length=50)
    media = models.FileField()
    timestamp = models.DateField(auto_now_add=True)
