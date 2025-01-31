from __future__ import print_function
import glob
import os
import re
import os.path as osp
import argparse
from convert_tfrecord import extract_frame, WAYMO_CLASSES

parser = argparse.ArgumentParser()
parser.add_argument('split', choices=['training', 'validation'])
parser.add_argument('--out-dir', default='./tmp')
parser.add_argument('--resize', default=0.5625, type=float)
args = parser.parse_args()

url_template = 'gs://waymo_open_dataset_v_1_4_0/archived_files/{split}/{split}_%04d.tar'.format(split=args.split)
if not os.path.exists(args.out_dir):
    os.mkdir(args.out_dir)
if args.split == 'training':
    num_segs = 32
    tf_path = osp.join(args.out_dir, args.split)
    if not os.path.exists(tf_path):
        os.mkdir(tf_path)
elif args.split == 'validation':
    num_segs = 8
    tf_path = osp.join(args.out_dir, args.split)
    if not os.path.exists(tf_path):
        os.mkdir(tf_path)
elif args.split == 'testing':
    num_segs = 8
    tf_path = osp.join(args.out_dir, args.split)
    if not os.path.exists(tf_path):
        os.mkdir(tf_path)
else:
    raise NotImplementedError(f'{args.split} is not supported')

begin_seg_id = 0
inter_file =  glob.glob(osp.join(args.out_dir, f'{args.split}_*.tar_.gstmp'))
if len(inter_file)>0:
    inter_file = sorted(inter_file)[0]
    begin_seg_id = re.findall('\d{4}', osp.basename(inter_file))
    begin_seg_id = int(begin_seg_id[0])

# clip_id = len(glob.glob('labels/*.txt'))
for seg_id in range(begin_seg_id, num_segs):
    flag = os.system('gsutil cp ' + url_template % seg_id + ' ' + args.out_dir)
    assert flag == 0, 'Failed to download segment %d. Make sure gsutil is installed'%seg_id
    os.system('cd %s; tar xf %s_%04d.tar -C %s'%(args.out_dir, args.split, seg_id, tf_path))
    # tfrecords = sorted(glob.glob('%s/*.tfrecord'%args.out_dir))
    # for record in tfrecords:
    #     extract_frame(record, 'labels/%05d.txt'%clip_id, 'images/%05d'%clip_id, WAYMO_CLASSES, resize_ratio=args.resize)
    #     print("Clip %d done"%clip_id)
    #     clip_id += 1
    #     os.remove(record)
    print("Segment %d done"%seg_id)
    os.remove(osp.join(args.out_dir, '%s_%04d.tar'%(args.split, seg_id)))
