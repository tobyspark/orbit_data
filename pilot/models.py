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
        
class Participant(models.Model):
    id = models.IntegerField(
        primary_key=True,
        default=mint_id,
        )
    email = models.EmailField(
        unique=True,
        )
    name = models.CharField(
        max_length=128,
        )
    survey_started = models.DateTimeField(
        null=True,
        )
    survey_token = models.CharField(
        default=mint_token,
        max_length=TOKEN_BYTES * 2, # average base64 encoding = 1.3x
        unique=True,
        )
    
    @property
    def survey_done(self):
        return Survey.objects.filter(participant=self).exists()
    


class SurveyManager(models.Manager):
    def create_survey(self, participant, fields):
        '''
        Create and save a survey entry, encrypting the supplied fields as a binary blob.
        As data to encrypt is of an unknown size, strategy is to use AES to encrypt the data, and RSA to encrypt the AES key.
        '''
        
        # Transform survey data (a dict) into bytes
        data = json.dumps(fields).encode('utf-8')
        
        # Get keys
        public_key = RSA.import_key(settings.PII_KEY_PUBLIC)
        aes_key = secrets.token_bytes(32) # AES-256, i.e. 256/8=32
        
        # Encrypt the AES 'session' key with the public RSA key
        cipher_rsa = PKCS1_OAEP.new(public_key)
        enc_aes_key = cipher_rsa.encrypt(aes_key)
        
        # Encrypt the data using AES
        cipher_aes = AES.new(aes_key, AES.MODE_EAX)
        ciphertext, mac_tag = cipher_aes.encrypt_and_digest(data)
        
        survey = self.create(
            participant=participant,
            enc_aes_key = enc_aes_key,
            aes_nonce = cipher_aes.nonce,
            aes_mac_tag = mac_tag,
            aes_ciphertext = ciphertext,
            )
        

class Survey(models.Model):
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        )
    enc_aes_key = models.BinaryField(max_length=16)
    aes_nonce = models.BinaryField(max_length=16)
    aes_mac_tag = models.BinaryField(max_length=16)
    aes_ciphertext = models.BinaryField()
    
    objects = SurveyManager()
    
    def __str__(self):
        return f"Survey for Participant {self.participant.id}"
        
    def decrypt(self):
        private_key_pem = settings.PII_KEY_PRIVATE
        if private_key_pem is None:
            print('Attempting to decrypt without private key')
            return None
            
        private_key = RSA.import_key(private_key_pem)
        
        # Decrypt the AES 'session' key with the private RSA key
        cipher_rsa = PKCS1_OAEP.new(private_key)
        aes_key = cipher_rsa.decrypt(self.enc_aes_key)
        
        # Decrypt the data with the AES session key
        cipher_aes = AES.new(aes_key, AES.MODE_EAX, self.aes_nonce)
        data = cipher_aes.decrypt_and_verify(self.aes_ciphertext, self.aes_mac_tag)
        
        # Transform back into fields
        fields = json.loads(data.decode("utf-8"))
        
        return fields

class LabelledMedia(models.Model):
    label = models.CharField(max_length=50)
    media = models.FileField()
    timestamp = models.DateField(auto_now_add=True)
