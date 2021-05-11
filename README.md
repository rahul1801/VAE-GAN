# VAE-GAN
The VAE-GAN implementation in Keras was carried out as a part of my research internship under the guidance of Prof. Brendan Mccane at the University of Otago, New Zealand. 

## VAE-GAN Architecture
The VAE-GAN Architecture implementation is consistent with the details metioned in the paper "Autoencoding beyond pixels using a learned similarity metric". 

<img width="294" alt="vae_gan_arch" src="https://user-images.githubusercontent.com/31514957/117771242-85197580-b253-11eb-8013-caf8bccd96cf.PNG">


### Architecture for Encoder Training
<img width="466" alt="encoder_train" src="https://user-images.githubusercontent.com/31514957/117772912-500e2280-b255-11eb-908e-719e050d66d8.PNG">

### Architecture for Decoder Training
<img width="788" alt="decoder_train" src="https://user-images.githubusercontent.com/31514957/117773097-8cda1980-b255-11eb-8f71-93621c9e75e1.PNG">

### Discriminator Architecture
<img width="855" alt="discriminator" src="https://user-images.githubusercontent.com/31514957/117773304-c4e15c80-b255-11eb-9378-5f9bc59ffca9.PNG">

## VAE-GAN Outputs
The model was trained on the MNIST and CelebA Dataset. The model was trained only for 60-70 epochs due to the limited GPU computational time offered by Google Colaboratory.

### MNIST Reconstructions
<img width="316" alt="mnist_out" src="https://user-images.githubusercontent.com/31514957/117773917-88fac700-b256-11eb-8e96-dab7deb4ffa7.PNG">

### CelebA Reconstructions
<img width="316" alt="vae_gan_out" src="https://user-images.githubusercontent.com/31514957/117774112-c52e2780-b256-11eb-8cd2-ddd941c39a74.PNG">

## Implementation References
The following resources have been extremely beneficial in helping me understand several implementation level details abstracted in the original paper.

1) [Darwin Bautista's VAE-GAN implementation](https://github.com/baudm/vaegan-celebs-keras)
2) [VAE-GAN official implementation](https://github.com/andersbll/autoencoding_beyond_pixels)
