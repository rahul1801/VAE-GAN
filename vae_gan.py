import numpy as np
%tensorflow_version 1.x
import tensorflow as tf

from google.colab import drive
drive.mount('/content/gdrive')
!unzip -q "/content/gdrive/My Drive/Colab Notebooks/img_align_celeba.zip"

from keras.models import Sequential, Model
from keras.layers import Input, Dense, LeakyReLU, BatchNormalization, ReLU,Lambda,Reshape
from keras.layers import Conv2D, Conv2DTranspose, Reshape, Flatten,Dropout
from keras.optimizers import Adam,RMSprop,Adagrad
from keras import initializers
from keras.utils import plot_model
from keras import backend as K
from IPython.display import Image,display
import matplotlib.pyplot as plt
from keras.losses import mean_squared_error
import os, sys
import cv2
import skimage.io as io

# cropping 30k images from the CelebA dataset into size (64x64) and splitting them into train (80%) and test (20%)
x = []
x_test = []
y = []
y_test = []
width,height = 64,64
img_path = '/content/img_align_celeba'
images = sorted(os.listdir(img_path))
idx = 0
cnt = 1
for i in range(len(images)):
  f = cv2.imread(img_path+'/'+images[i])
  if cnt <= 24000:
    pass
    x.append(f.copy())
  else:
    pass
    x_test.append(f.copy())
  cnt+=1
  if (cnt>30000):
    break
for i in range(len(x)):
  x[i] = cv2.resize(x[i],(width,height))
for j in range(len(x_test)):
  x_test[j] = cv2.resize(x_test[j],(width,height))
X_train = np.array(x)
X_test = np.array(x_test)

print(X_train.shape)
print(X_test.shape)

class vae_gan_celeb:
  def __init__(self):
    # processing images and initializing hyperparameters for the VAE-GAN
    self.x_train = X_train
    self.x_test = X_test
    self.x_train = self.x_train.astype('float32')/255
    self.x_test = self.x_test.astype('float32')/255
    self.x_train = self.x_train.reshape(self.x_train.shape[0],64,64,3)
    self.x_test = self.x_test.reshape(self.x_test.shape[0],64,64,3)
    self.epochs = 300
    self.batch_size = 250
    self.optimizer = RMSprop(lr=0.0003)
    #self.optimizer = Adagrad(lr=0.01)
    self.init = initializers.RandomNormal(stddev=0.02)
    
  def convert(self,args):
    z_log_var = args
    z_sigma = K.exp(0.5*(z_log_var))
    return z_sigma
  
  def sample(self,args):
    z_mean,z_sigma = args
    epsilon = K.random_normal(shape=(K.shape(self.input_img)[0],2048),mean=0,stddev=1)
    z = z_mean + z_sigma*epsilon
    return z
    
  def vae_gan(self):
    # encoder
    self.input_img = Input(shape=(64,64,3,))
    conv1 = Conv2D(64,kernel_size=5,activation='relu',strides=2)(self.input_img)
    batch_norm1 = BatchNormalization(momentum=0.8)(conv1)
    conv2 = Conv2D(128,kernel_size=5,activation='relu',strides=2)(batch_norm1)
    batch_norm2 = BatchNormalization(momentum=0.8)(conv2)
    conv3 = Conv2D(256,kernel_size=5,activation='relu',strides=2)(batch_norm2)
    batch_norm3 = BatchNormalization(momentum=0.8)(conv3)
    dense_layer = Flatten()(batch_norm3)
    z_mean = Dense(2048,activation='relu')(dense_layer)
    z_mean_bn = BatchNormalization(momentum=0.8)(z_mean)
    z_log_var = Dense(2048)(dense_layer)
    z_sigma = Lambda(self.convert)(z_log_var)
    z = Lambda(self.sample)([z_mean_bn,z_sigma])

    self.encoder = Model(self.input_img,[z,z_mean_bn,z_sigma])
    plot_model(self.encoder,to_file='demo.png',show_shapes=True,show_layer_names=True)
    display(Image(filename='demo.png'))
    
    # decoder
    self.latent_input = Input(shape=(2048,))
    dense_layer_dec = Dense(8*8*256)(self.latent_input)
    dense_layer_dec_bn = BatchNormalization(momentum=0.8)(dense_layer_dec)
    dec_img = Reshape((8,8,256))(dense_layer_dec_bn)
    deconv1 = Conv2DTranspose(256,kernel_size=3,strides=2,activation='relu')(dec_img)
    batch_norm1_dec = BatchNormalization(momentum=0.8)(deconv1)
    deconv2 = Conv2DTranspose(128,kernel_size=2,strides=2,activation='relu')(batch_norm1_dec)
    batch_norm2_dec = BatchNormalization(momentum=0.8)(deconv2)
    deconv3 = Conv2DTranspose(32,kernel_size=2,activation='relu',strides=2)(batch_norm2_dec)
    batch_norm3_dec = BatchNormalization(momentum=0.8)(deconv3)
    dec_output = Conv2D(3,kernel_size=5,activation='tanh')(batch_norm3_dec)
    
    self.decoder = Model(self.latent_input,dec_output)
    plot_model(self.decoder,to_file='demo2.png',show_shapes=True,show_layer_names=True)
    display(Image(filename='demo2.png'))
    
    # discriminator
    self.real_input = Input(shape=(64,64,3,))
    conv1_dis = Conv2D(32,kernel_size=5,activation='relu',strides=2)(self.real_input)
    conv2_dis = Conv2D(128,kernel_size=5,activation='relu',strides=2)(conv1_dis)
    batch_norm1_dis = BatchNormalization(momentum=0.8)(conv2_dis)
    conv3_dis = Conv2D(256,kernel_size=5,activation='relu',strides=2)(batch_norm1_dis)
    batch_norm2_dis = BatchNormalization(momentum=0.8)(conv3_dis)
    conv4_dis = Conv2D(256,kernel_size=5,activation='relu',strides=2)(batch_norm2_dis)
    batch_norm3_dis = BatchNormalization(momentum=0.8)(conv4_dis)
    dense_layer_dis = Flatten()(batch_norm3_dis)
    fc_dis = Dense(512,activation='relu')(dense_layer_dis)
    fc_dis_bn = BatchNormalization(momentum=0.8)(fc_dis)
    dis_output = Dense(1,activation='sigmoid')(fc_dis_bn)
    
    self.discriminator = Model(self.real_input,[dis_output,fc_dis_bn])
    plot_model(self.discriminator,to_file='demo3.png',show_shapes=True,show_layer_names=True)
    display(Image(filename='demo3.png'))
    
    #vae model for testing
    self.dec_output = self.decoder(self.encoder(self.input_img)[0])
    self.vae_model = Model(self.input_img,self.dec_output)
    print("")
    print("VAE")
    print("")
    plot_model(self.vae_model,to_file='demo4.png',show_shapes=True,show_layer_names=True)
    display(Image(filename='demo4.png'))
    
    # Connecting the graphs to construct the VAE-GAN as mentioned in the paper "Autoencoding beyond pixels using a learned similarity metric"
    z,z_mean,z_sigma = self.encoder(self.input_img)
    x_enc = self.decoder(z)
    x_dec = self.decoder(self.latent_input)
    dis_real,disl_x = self.discriminator(self.input_img)
    dis_out_enc,disl_x_enc = self.discriminator(x_enc)
    dis_out_dec = self.discriminator(x_dec)[0]
    
    # initializing models for network-wise training
    encoder_training = Model(self.input_img,disl_x_enc)
    decoder_training = Model([self.input_img,self.latent_input],[dis_out_enc,dis_out_dec])
    discriminator_training = Model([self.input_img,self.latent_input],[dis_out_enc,dis_real,dis_out_dec])
    
    real_img_score = np.full((self.batch_size,1),fill_value=1)
    fake_img_score = np.full((self.batch_size,1),fill_value=0)
    
    real_img_score = tf.convert_to_tensor(real_img_score + 0.05*np.random.random(real_img_score.shape),dtype='float32')
    fake_img_score = tf.convert_to_tensor(fake_img_score + 0.05*np.random.random(fake_img_score.shape),dtype='float32')
    
    self.decoder.trainable = False
    self.discriminator.trainable = False
    self.encoder.trainable = True
    
    loss1 = K.mean(K.square(z_sigma) + K.square(z_mean_bn) - K.log(z_sigma) - 1)
    loss2 = 0.5*(mean_squared_error(K.flatten(disl_x),K.flatten(disl_x_enc)))
    loss = loss1 + loss2
    encoder_training.add_loss(loss)
    encoder_training.compile(optimizer=self.optimizer)
    
    self.encoder.trainable = False
    self.decoder.trainable = True
    
    loss3 = K.binary_crossentropy(dis_out_enc,real_img_score,from_logits=True)
    loss4 = K.binary_crossentropy(dis_out_dec,real_img_score,from_logits=True)
    loss_dec = 64*loss2 + loss3 + loss4
    decoder_training.add_loss(loss_dec)
    decoder_training.compile(optimizer=self.optimizer)
    
    self.decoder.trainable = False
    self.discriminator.trainable = True
    
    loss5 = K.binary_crossentropy(dis_out_enc,fake_img_score,from_logits=True)
    loss6 = K.binary_crossentropy(dis_real,real_img_score,from_logits=True)
    loss7 = K.binary_crossentropy(dis_out_dec,fake_img_score,from_logits=True)
    loss_dis = loss5 + loss6 + loss7
    discriminator_training.add_loss(loss_dis)
    discriminator_training.compile(optimizer=self.optimizer)
    
    num_of_batches = int(len(self.x_train)/self.batch_size)
    
    for e in range(self.epochs+1):
      a = 0
      b = self.batch_size
      for i in range(num_of_batches):
        real_images = self.x_train[a:b,:,:,:]
        z = np.random.normal(0,1,(self.batch_size,2048))
        z1 = np.random.normal(0,1,(11,2048))
        
        self.encoder.trainable = False
        self.decoder.trainable = False
        self.discriminator.trainable = True
        
        dis_loss = discriminator_training.train_on_batch([real_images,z],None)
        
        self.discriminator.trainable = False
        self.decoder.trainable = True
        
        dec_loss = decoder_training.train_on_batch([real_images,z],None)
        
        self.decoder.trainable = False
        self.encoder.trainable = True
        
        enc_loss = encoder_training.train_on_batch(real_images,None)
        
        if(i%20==0):
          print('Epoch: '+str(e+1))
          print('Batch Number: '+str(i+1))
          print('Encoder Loss')
          print(enc_loss)
          print('Decoder Loss')
          print(dec_loss)
          print('Discriminator Loss')
          print(dis_loss)
          print("")
