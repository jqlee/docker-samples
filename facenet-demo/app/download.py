import argparse
import os
import sys
import download_and_extract as de


def main(args):
    if not os.path.exists(os.path.join(args.data_path, args.model)):
        download_model(args.model, args.data_path)

    #download_lfw(args.data_path)

    
def download_model(model, path):
    de.download_and_extract_file(model, path)

def download_lfw(path):
    import requests

    url = "http://vis-www.cs.umass.edu/lfw/lfw.tgz"
    filename = os.path.join(path,url.split("/")[-1])
    if not os.path.exists(filename):
        print('Downloading file to {}'.format(filename))
        r = requests.get(url)
    
        with open(filename, "wb") as f:
            print('Extracting file to {}'.format(path))
            f.write(r.content)
    

def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--model', type=str, default='20180402-114759', 
        help='Could be either a directory containing the meta_file and ckpt_file or a model protobuf (.pb) file')
    parser.add_argument('--data_path', type=str, default='/data',
        help='Target folder to download and extrace files')
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