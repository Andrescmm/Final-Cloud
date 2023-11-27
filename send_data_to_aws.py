
from flask import Flask, render_template, request, jsonify
import requests
import os
import random
import boto3
import json
app = Flask(__name__)
from werkzeug.utils import secure_filename

s3 = boto3.client('s3',
                    aws_access_key_id= "ASIATWNVL6UCPBS7KRQC",
                    aws_secret_access_key= "8JU1JSLEG3SeSQKURBL2XMrPwLrRmLimF5xuSzRC",
                    aws_session_token= "FwoGZXIvYXdzEGEaDJ6TVvrNabymf954uSKCAc2Yo8ri/Me7eMw9tjAk+0z8JEgUFuLCupQDhrs2mTN5ZhX5GZtZNEQAIQ0cbSLTV+3IS7xZkMpfhacx0N3tLNUpmlggQ86e0roVJUbHfl0Emfc6Q4pUGTXqnhVURkx4pxIGff0geR9S8vlARtWGecbSszwclHZ0FAQbuD98+eb8rdQolfiSqwYyKLFbJZJzCPPihZc/HK0A+UIvppbdgwxEwGksWlV7Y2g5sPG0DVcvZ0A="
                     )


BUCKET_NAME='videostorageandresources'
AWS_LAMBDA_ENDPOINT = 'https://4odr9y9p54.execute-api.us-east-1.amazonaws.com/default/bestfunctionintheworld'


def get_videos_from_s3(query_key):
    bucket_name = 'videostorageandresources'
    folder_prefix = 'video/'
    file_key = 'output_inverted_index_dictionary_objects.json'
    print("get_videos_from_s3 ")
    try:
        print("try ")
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        content = response['Body'].read().decode('utf-8')
        data = json.loads(content)

        # Assuming data is a dictionary with keys as query and values as video filenames
        if query_key in data:
            video_names = data[query_key]
            videos = []

            # Get signed URLs for videos from S3 within the 'videos' folder
            for video_name in video_names:
                full_video_key = folder_prefix + video_name
                print("Video name:", video_name)
                video_url = s3.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': bucket_name, 'Key': full_video_key},
                    ExpiresIn=3600000  # Adjust the expiration time as needed
                )
                videos.append(video_url)

            return videos
        else:
            return []
    except Exception as e:
        return str(e)
    
def get_keys():
    bucket_name = 'videostorageandresources'
    file_key = 'output_inverted_index_dictionary_objects.json'
    print(get_keys)
    try:
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        content = response['Body'].read().decode('utf-8')

        # Parsea el contenido del archivo JSON
        data = json.loads(content)

        # Obtiene las claves del diccionario
        keys = list(data.keys())
        print(keys)

        # Retorna aleatoriamente 3 claves
        return random.sample(keys, 3)
    
    except Exception as e:
        return f"Error: {str(e)}"
    
def get_all_videos_from_s3():
    bucket_name = 'videostorageandresources'
    folder_prefix = 'video/'
    file_key = 'output_inverted_index_dictionary_objects.json'
    try:
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        content = response['Body'].read().decode('utf-8')
        
        data = json.loads(content)

        all_videos = set() 

        # Iterate over all keys in the data 

        for key in data:
            video_names = data[key]
            for video_name in video_names:
                full_video_key = folder_prefix + video_name
                video_url = s3.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': bucket_name, 'Key': full_video_key},
                    ExpiresIn=3600  # Adjust the expiration time as needed
                )
                all_videos.add(video_url)

        return list(all_videos)
    except Exception as e:
        return str(e)


@app.route('/search', methods=['GET'])
def search():
    query_key = request.args.get('key_to_search')
    if query_key:
        # Verificar si todas las letras están en mayúsculas
        if query_key.isupper():
            query_key = query_key.lower()
            query_key = query_key.capitalize()
        else:
            words = query_key.split()
            if len(words) > 1:
                query_key = words[0].capitalize() + ' ' + words[1].lower()
            else:
                query_key = query_key.capitalize()
        
    videos = get_videos_from_s3(query_key)

    if videos:
        return render_template('results.html', videos=videos, query_key=query_key)
    else:
        return render_template('results.html', videos=videos, query_key=query_key)


@app.route('/')  
def home():
    videos = get_all_videos_from_s3()
    random_keys = get_keys()
    print(random_keys)
    videos1 = get_videos_from_s3(random_keys[0])
    videos2 = get_videos_from_s3(random_keys[1])
    videos3 = get_videos_from_s3(random_keys[2])
    if random_keys:
        return render_template('file_upload_to_s3.html',videos = videos, key1= random_keys[0],videos1=videos1,key2= random_keys[1],videos2=videos2,key3= random_keys[2], videos3=videos3)

    else:
        return render_template("file_upload_to_s3.html",videos = videos)


@app.route('/upload',methods=['post'])
def upload():
    if request.method == 'POST':
        img = request.files['file']
        if img:
                filename = secure_filename(img.filename)
                key = 'video/' + filename
                img.save(filename)
                s3.upload_file(
                    Bucket = BUCKET_NAME,
                    Filename=filename,
                    Key = key
                )
                msg = "Upload Done ! "
                
    videos = get_all_videos_from_s3()
    random_keys = get_keys()
    print(random_keys)
    videos1 = get_videos_from_s3(random_keys[0])
    videos2 = get_videos_from_s3(random_keys[1])
    videos3 = get_videos_from_s3(random_keys[2])
    if random_keys:
        return render_template('file_upload_to_s3.html',msg =msg,videos = videos, key1= random_keys[0],videos1=videos1,key2= random_keys[1],videos2=videos2,key3= random_keys[2], videos3=videos3)

    else:
        return render_template("file_upload_to_s3.html",msg =msg, videos = videos)

if __name__ == "__main__":
    app.run(host=os.getenv('IP', '0.0.0.0'), 
            port=int(os.getenv('PORT', 4444)))
    



