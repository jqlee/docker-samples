"""Performs face alignment and calculates L2 distance between the embeddings of images."""

# MIT License
# 
# Copyright (c) 2016 David Sandberg
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from scipy import misc
import tensorflow as tf
import numpy as np
import sys
import os
import copy
import argparse
import facenet
import align.detect_face

global_data_path = ''

def main(args):
    global global_data_path
    global_data_path = args.data_path
    # "--data_path=/data",
    # "--model=20180402-114759",
    # "--photo_path=/data/tmp/",
    # "--target_file=022.jpg"

    from os import listdir
    from os.path import isfile, join
    
    photo_path = abs_datapath(args.photo_dir)
    image_files = [os.path.join(photo_path,f) for f in listdir(photo_path) if isfile(join(photo_path, f))]

    # 將比對目標整理到第一個，方便後續程式處理
    target_index = image_files.index(os.path.join(photo_path, args.target_file))
    #target = image_files.pop(target_index)
    #image_files.insert(0, target)

    # print(image_files)
    images = load_and_align_data(image_files, args.image_size, args.margin, args.gpu_memory_fraction)
    with tf.Graph().as_default():

        with tf.Session() as sess:

            # Load the model
            facenet.load_model(abs_datapath(args.model))

            # Get input and output tensors
            images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
            embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
            phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")

            # Run forward pass to calculate embeddings
            feed_dict = { images_placeholder: images, phase_train_placeholder:False }
            emb = sess.run(embeddings, feed_dict=feed_dict)

            
            #emb.dump(abs_datapath('emp.pk'))
            import pickle # 比直接dump小33%
            with open(abs_datapath('emp.pk1'), 'wb') as handle:
                pickle.dump(emb, handle, protocol=pickle.HIGHEST_PROTOCOL)            

            nrof_images = len(image_files)

            print('')
            
            print('比對標的: {}'.format(args.target_file))
            # print('')
            # print('標的圖片與其他圖片的特徵值距離:')
            nearlist = []
            j = 0
            for i in range(nrof_images):
                if i == target_index: continue # 跳過跟自己比對
                dist = np.sqrt(np.sum(np.square(np.subtract(emb[i,:], emb[target_index,:]))))
                dist_text = dist if dist < 1 else 1 - dist
                # print('{}: {}'.format(args.image_files[i], dist_text))
                name = image_files[i]
                nearlist.append({'name':name,'dist':dist, 'confidence': getConfidence(dist)})

            candidates = [elem for elem in nearlist if elem['confidence'] > 50]
            results = sorted(candidates, key = lambda x:x['confidence'], reverse=True)
            # results = sorted(nearlist, key= lambda x:x['dist'], reverse=True)
            print('')
            print('候選項目:')
            print('')
            for kvp in results:
                print('"{}" 信心指數: {}'.format(kvp['name'], kvp['confidence'])) 

def abs_datapath(filename):
    return os.path.join(global_data_path, filename)
                
def getConfidence(dist, m=0.3, n=1.0):
    #對單一照片的信心指數
    #特徵值之間的距離，越小表示越相似
    #相同人不同照片的特徵距離一般在1以下，完全相同的照片距離為0
    #m = 0.3
    #n = 1.1
    maxd = 1.5
    if dist < m:
        # 0 ~ m
        return 95.0 + (5/m)*(m-dist);
    else:
        if dist >= m and dist < n:
            # m ~ n
            return 50.0+(45/(n-m))*(n-dist)
        else:
            # > n
            return (50.0/(maxd-n))*(maxd-dist)

def load_and_align_data(image_paths, image_size, margin, gpu_memory_fraction):

    minsize = 20 # minimum size of face
    threshold = [ 0.6, 0.7, 0.7 ]  # three steps's threshold
    factor = 0.709 # scale factor
    
    print('Creating networks and loading parameters')
    with tf.Graph().as_default():
        gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=gpu_memory_fraction)
        sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False))
        with sess.as_default():
            pnet, rnet, onet = align.detect_face.create_mtcnn(sess, None)
  
    tmp_image_paths=copy.copy(image_paths)
    img_list = []
    for image in tmp_image_paths:
        img = misc.imread(os.path.expanduser(image), mode='RGB')
        img_size = np.asarray(img.shape)[0:2]
        bounding_boxes, _ = align.detect_face.detect_face(img, minsize, pnet, rnet, onet, threshold, factor)
        if len(bounding_boxes) < 1:
          image_paths.remove(image)
          print("can't detect face, remove ", image)
          continue
        det = np.squeeze(bounding_boxes[0,0:4])
        bb = np.zeros(4, dtype=np.int32)
        bb[0] = np.maximum(det[0]-margin/2, 0)
        bb[1] = np.maximum(det[1]-margin/2, 0)
        bb[2] = np.minimum(det[2]+margin/2, img_size[1])
        bb[3] = np.minimum(det[3]+margin/2, img_size[0])
        cropped = img[bb[1]:bb[3],bb[0]:bb[2],:]
        aligned = misc.imresize(cropped, (image_size, image_size), interp='bilinear')
        prewhitened = facenet.prewhiten(aligned)
        img_list.append(prewhitened)
    images = np.stack(img_list)
    return images

def parse_arguments(argv):

    parser = argparse.ArgumentParser()
    
  
    parser.add_argument('--data_path', type=str, default="/data",
        help='')
    parser.add_argument('--model', type=str, default="20180402-114759",
        help='')
    parser.add_argument('--photo_dir', type=str, default="/data/samples/",
        help='')
    parser.add_argument('--target_file', type=str, default="022.jpg",
        help='')
    parser.add_argument('--image_size', type=int,
        help='Image size (height, width) in pixels.', default=160)
    parser.add_argument('--margin', type=int,
        help='Margin for the crop around the bounding box (height, width) in pixels.', default=44)
    parser.add_argument('--gpu_memory_fraction', type=float,
        help='Upper bound on the amount of GPU memory that will be used by the process.', default=1.0)
    return parser.parse_args(argv)

if __name__ == '__main__':

    import platform # print os
    print('OS:{}, platform:{}, release:{}'.format(os.name, platform.system(), platform.release()))
    main(parse_arguments(sys.argv[1:]))
