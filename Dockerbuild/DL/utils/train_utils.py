#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: giacomo.nodjoumi@hyranet.info - g.nodjoumi@jacobs-university.de
"""
from colour import Color
import detectron2
from detectron2.data.datasets import register_coco_instances
from detectron2.data import MetadataCatalog
import labelme2coco
import os
import pandas as pd
from sklearn.model_selection import train_test_split
import shutil



def label2coco():
    json_path = './custom_dataset.json'
    image_path = '../data'
    labelme2coco.convert(image_path, json_path)
    train_dir = image_path+'/train'
    dataset_name = 'custom_dataset'
    os.makedirs(train_dir, exist_ok=True)
    return(dataset_name, image_path, json_path, train_dir)

def classDump(meta,train_dir):
    #Dump classes
    classes = meta.thing_classes
    class_file = train_dir +'/trained_classes.csv'
    ddf = pd.DataFrame(classes)
    ddf.to_csv(class_file, index=False)
    return(classes)

def datasetReg():
    dataset_name, image_path, json_path, train_dir = label2coco()
    dataset = detectron2.data.datasets.load_coco_json(json_path,
                        image_path, dataset_name)
    register_coco_instances(dataset_name, {}, json_path, image_path)
    meta = MetadataCatalog.get(dataset_name)
    classes = classDump(meta, train_dir)
    blue = Color("blue")
    green = Color("green")
    colors = list(blue.range_to(green, len(classes)))
    meta.set(thing_colors=colors)
    return(dataset, meta, classes, train_dir, image_path)


def data_split(dataset):
    train, test = train_test_split(dataset, test_size=0.1, random_state=1,shuffle=True)
    train, valid = train_test_split(train, test_size=0.3, random_state=1,shuffle=True)
    #test=None
    return(train, valid, test)

def categories_gen(dataset):
    categories = []
    for d in dataset:
        for ann in d['annotations']:
            categories.append(ann['category_id'])
    return(categories)


def classes_distribution(categories, datatype, classes):
    classes_dis=[]
    for cat in categories:
    #    print(classes[cat])
        classes_dis.append(classes[cat])
    classes_dis =list(zip(classes_dis,[datatype for i in range(len(classes_dis))]))
    df_dis = pd.DataFrame(classes_dis, columns=['Class','Dataset'])
    
    return(df_dis)

def dataframes_gen(classes, dataset):
    train, valid, test = data_split(dataset)
    train_categories = categories_gen(train)
    train_df_dis = classes_distribution(train_categories, 'Train', classes)
    
    valid_categories = categories_gen(valid)
    valid_df_dis = classes_distribution(valid_categories, 'Valid', classes)
    
    test_categories = categories_gen(test)
    test_df_dis = classes_distribution(test_categories, 'Test', classes)
    return(train_df_dis, valid_df_dis, test_df_dis, train, valid, test)


def dataMover(image_path, train, valid, test):
    ### TRAIN DATASET
    train_data_path = image_path+'/train_data'
    os.makedirs(train_data_path, exist_ok=True)
    for i in range(len(train)):
        file = train[i]['file_name']
        basename = os.path.basename(file.split('.tiff')[0])
        src_dir = os.path.dirname(file)
        shutil.copy(src_dir+'/'+basename+'.tiff',  train_data_path+'/'+basename+'.tiff')
        shutil.copy(src_dir+'/'+basename+'.json',  train_data_path+'/'+basename+'.json')
        train_file = train_data_path+'/train_data.json'
    labelme2coco.convert(train_data_path, train_file)
    train_dataset = detectron2.data.datasets.load_coco_json(train_file,
                            '', 'train_data')
    register_coco_instances("train_data", {}, train_file, '')
    
    
    ### VALID DATASET
    valid_data_path = image_path+'/valid_data'
    os.makedirs(valid_data_path, exist_ok=True)
    for i in range(len(valid)):
        file = valid[i]['file_name']
        basename = os.path.basename(file.split('.tiff')[0])
        src_dir = os.path.dirname(file)
        dst_dir = valid_data_path
        shutil.copy(src_dir+'/'+basename+'.tiff', dst_dir+'/'+basename+'.tiff')
        shutil.copy(src_dir+'/'+basename+'.json', dst_dir+'/'+basename+'.json')
    valid_file = valid_data_path+'/valid_data.json'
    labelme2coco.convert(valid_data_path, valid_file)
    valid_dataset = detectron2.data.datasets.load_coco_json(valid_file,
                        '', 'valid_data')
    register_coco_instances("valid_data", {}, valid_file, '')    
    
        
    ### TEST DATASET
    test_data_path = image_path+'/test_data'
    os.makedirs(test_data_path, exist_ok=True)
    for i in range(len(valid)):
        file = valid[i]['file_name']
        basename = os.path.basename(file.split('.tiff')[0])
        src_dir = os.path.dirname(file)
        dst_dir = test_data_path
        shutil.copy(src_dir+'/'+basename+'.tiff', dst_dir+'/'+basename+'.tiff')
        shutil.copy(src_dir+'/'+basename+'.json', dst_dir+'/'+basename+'.json')
    valid_file = test_data_path+'/test_data.json'
    labelme2coco.convert(test_data_path, valid_file)
    test_dataset = detectron2.data.datasets.load_coco_json(valid_file,
                        '', 'test_data')
    register_coco_instances("test_data", {}, valid_file, '')    
        



