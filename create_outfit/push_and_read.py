import requests, os, io, json, base64
from pathlib import Path
import pymongo 
from PIL import Image
from bson import Binary
import matplotlib.pyplot as plt


client = pymongo.MongoClient(
"mongodb+srv://user:fqg78pXPCpt8dtk@cluster0.xzh33.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client.test
# print(db)

# Database Name 
db = client["images"] 
  
# Collection Name 
collection = db["filters"] 


filename='/home/dmytro/Projects/eleks_practice/label/keras-multi-label/dataset/dataset_for_site/bags'
# img = Image.open(filename)
# imgByteArr = io.BytesIO()
# img.save(imgByteArr, format='PNG')
# imgByteArr = imgByteArr.getvalue()




with open(filename, "rb") as imageFile:
    image_in_str = base64.b64encode(imageFile.read()) 
    emp_rec1 = { 
        "item":"bags", 
        # "percent":88,
		'tags': 
        "imageName":os.path.basename(filename),
        "img":image_in_str
        }
    rec_id1 = collection.insert_one(emp_rec1).inserted_id # save this in DB


# x = collection.find({'name': 'skirt'}) 

# for data in x:
#     imageName = data['imageName']
#     getImage = data['img']
#     with open(imageName, "wb") as f:
#         f.write(base64.decodestring(getImage))
























# USAGE
# Start the server:
# 	python flask_deploy.py
# Submit a request via cURL:
# 	curl -X POST -F image=@dog.jpg 'http://0.0.0.0:5000/predict'

# import the necessary packages
from keras.preprocessing.image import img_to_array, load_img
from keras.models import load_model
from PIL import Image
import numpy as np
import pickle, cv2, os, io, flask, pymongo, random


app = flask.Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
app.config['IMAGE_UPLOADS'] = os.path.join(APP_ROOT, 'uploads')
model_cat = None
model_sty = None
model_rec = None


@app.route("/predict", methods=["POST"])
def predict():
	# ensure an image was properly uploaded to our endpoint
	res={}
	res["feedback"] = []
	if flask.request.method == "POST":
		# if (flask.request.headers.get("Authorization") == "Basic YWxhZGRpbjpvcGVuc2VzYW1lljrhebgervwekbflisufbewyufewfsngsdbgrrldngsufigbeurgb"):
		if flask.request.files.get("image"):
			result_5={}
			result_5['item'] = []
			result_5['tags'] = []
			res["predictions"] = []
			# read the image in PIL format	
			image = flask.request.files["image"]
			filename = image.filename
			file_path = os.path.join(app.config["IMAGE_UPLOADS"], filename)
			image_pil = Image.open(image)
			image_pil.save(file_path)
			image = load_img(file_path, target_size=(96,96))
			image = cv2.imread(file_path)
			image = cv2.resize(image, (96, 96))
			image = image.astype("float") / 255.0
			image = img_to_array(image)
			image = np.expand_dims(image, axis=0)

			# classify the input image then find the indexes of the two class
			# labels with the *largest* probability
			print("[INFO] classifying image...")
			proba_cat = model_cat.predict(image)[0]
			idxs_cat = np.argsort(proba_cat)[::-1][:2]  # return 2 results from categories model
			proba_sty = model_sty.predict(image)[0]
			idxs_sty = np.argsort(proba_sty)[::-1][:4]  # return 4 results from styles model
			proba_rec = model_rec.predict(image)[0]
			idxs_rec = np.argsort(proba_rec)[::-1][:1]  # return 2 results from categories model


			# loop over the indexes of the high confidence class labels
			for (i, j) in enumerate(idxs_rec):
				# build the label and draw the label on the image
				# result_5.append("{}: {:.2f}%".format(mlb_cat.classes_[j], proba_cat[j] * 100))
				result_5['item'] = mlb_rec.classes_[j]

			# loop over the indexes of the high confidence class labels
			for (i, j) in enumerate(idxs_cat):
				# build the label and draw the label on the image
				# result_5.append("{}: {:.2f}%".format(mlb_cat.classes_[j], proba_cat[j] * 100))
				result_5['tags'].append(mlb_cat.classes_[j])
				# r = {"label": "{}".format(mlb_cat.classes_[j]), "probability": "{:.2f}".format(proba_cat[j] * 100)}
				# res["predictions"].append(r)
			# loop over the indexes of the high confidence class labels
			for (i, j) in enumerate(idxs_sty):
				# build the label and draw the label on the image
				# result_5.append("{}: {:.2f}%".format(mlb_sty.classes_[j], proba_sty[j] * 100))
				result_5['tags'].append(mlb_sty.classes_[j])
				# r = {"label": "{}".format(mlb_sty.classes_[j]), "probability": "{:.2f}".format(proba_sty[j] * 100)}
				# res["predictions"].append(r)
		else:
			res['feedback'].append("Flask doesn't get image")
		# else:
		# 	res['feedback'].append("Authorization token is wrong")
	else: 
		res['feedback'].append("Request isn`t POST")

	# return the data dictionary as a JSON response
	print(result_5)
	return flask.jsonify(result_5)
	# return flask.jsonify(res)


@app.route("/recommend", methods=["POST"])
def recommend():
	# ensure an image was properly uploaded to our endpoint
	res={}
	res["feedback"] = []
	if flask.request.method == "POST":
		# if (flask.request.headers.get("Authorization") == "Basic YWxhZGRpbjpvcGVuc2VzYW1lljrhebgervwekbflisufbewyufewfsngsdbgrrldngsufigbeurgb"):
		itemTags = []
		item = ''

		item = flask.request.json['item']
		itemTags = flask.request.json['tags']
		databaseName = flask.request.headers.get("DbName")
		collectionName = flask.request.headers.get("CollName")

		# Connect to DataBase
		client = pymongo.MongoClient("mongodb+srv://user:fqg78pXPCpt8dtk@cluster0.xzh33.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
		# Database Name 
		db = client[databaseName] 
		# Collection Name 
		collection = db[collectionName]
		
		
		look1 = {'shoes': 50, 'dresses': 50, 'coats': 50, 'pants': 50, 'shorts': 50, 'sweaters': 50, 't-shirts': 50, 'bags': 30 }

		neededItems={}

		for clothElement, similarity in look1.items():
			neededItems[clothElement] = []
			x = collection.find({'name': clothElement})
			for data in x:
				# print(data)
				itemID = data['_id']
				filterName = data['name']
				imageName = data['imageName']
				getImage = data['img']
				getTags = data['tags']
				for k,v in itemTags.items():
					res = format((len(set(v) & set(getTags)) / float(len(set(v) | set(getTags))) * 100), ".0f")
					# print("Similarity is = " + str(res) + ' | ' + str(getTags))
					if(int(res) >= similarity):
						neededItems[clothElement].append(itemID)
						itemTags[itemID] = getTags
						os.makedirs(filterName, exist_ok=True)
						with open(filterName + '/' + imageName, "wb") as f:
							f.write(base64.decodestring(getImage))
		
		create_looks_from_single_item(neededItems, item)

		def create_looks_from_single_item(neededItems, item):
			shoes = {'look1': ["pants", "t-shirts"], 'look2': ["pants", "sweaters"], 'look3': ["shorts", "t-shirts"]}
			dresses = {'look1': ["shoes", "bags"], 'look2': ["shoes", "bags"], 'look3': ["shoes", "coats"]}
			coats = {'look1': ["shoes", "pants", "sweaters"], 'look2': ["shoes", "pants", "t-shirts"], 'look3': ["shoes", "pants", "sweaters"]}
			pants = {'look1': ["shoes", "t-shirts"], 'look2': ["shoes", "sweaters"], 'look3': ["shoes", "sweaters", "coats"]}
			shorts = {'look1': ["shoes", "t-shirts"], 'look2': ["shoes", "t-shirts"], 'look3': ["shoes", "t-shirts"]}
			sweaters = {'look1': ["shoes", "pants"], 'look2': ["shoes", "pants"], 'look3': ["shoes", "pants", "coats"]}
			t_shirts = {'look1': ["shoes", "pants"], 'look2': ["shoes", "pants"], 'look3': ["shoes", "shorts"]}
			look = {}
			

			if(item=="shoes"):
				generate_random_look(shoes, neededItems, look)
			if(item=="dresses"):
				generate_random_look(dresses, neededItems, look)
			if(item=="coats"):
				generate_random_look(coats, neededItems, look)
			if(item=="pants"):
				generate_random_look(pants, neededItems, look)
			if(item=="shorts"):
				generate_random_look(shorts, neededItems, look)
			if(item=="t_shirts"):
				generate_random_look(t_shirts, neededItems, look)
			if(item=="sweaters"):
				generate_random_look(sweaters, neededItems, look)
			# if(item=="skirts"):
			#     generate_random_look(shoes, neededItems, look)

			for k,v in look.items():
				print(str(k) + ": " + str(v))


		def generate_random_look(item, neededItems, look):
			for k,v in item.items():
				look[k] = []
				look[k].append('loadedImageID')
				for s in v:
					if(neededItems[s]==[]):
						look[k].append("Items doesn't fit!")
					else:
						rand_choice = random.choice(neededItems[s])
						look[k].append(rand_choice)
						
						x = collection.find({'_id': rand_choice})
						for data in x:
							filterName = data['name']
							imageName = data['imageName']
							getImage = data['img']
							
							os.makedirs(k, exist_ok=True)
							with open(k + '/' + imageName, "wb") as f:
								f.write(base64.decodestring(getImage))






		
	else: 
		res['feedback'].append("Request isn`t POST")

	# return the data dictionary as a JSON response
	print(result)
	return flask.jsonify(result)
	# return flask.jsonify(res)


@app.route("/")
def start():
	return "Hello, server works properly! \n Have a nice day)"


def load_models():
	global model_cat
	model_cat = load_model(APP_ROOT+"/models/categories_40_epochs.model")
	global mlb_cat
	mlb_cat = pickle.loads(open(APP_ROOT+"/models/categories_40_epochs.pickle", "rb").read())
	global model_sty
	model_sty = load_model(APP_ROOT+"/models/styles_40_epochs.model")
	global mlb_sty
	mlb_sty = pickle.loads(open(APP_ROOT+"/models/styles_40_epochs.pickle", "rb").read())
	global model_rec
	model_rec = load_model(APP_ROOT+"/models/cloth_recognition.model")
	global mlb_rec
	mlb_rec = pickle.loads(open(APP_ROOT+"/models/cloth_recognition.pickle", "rb").read())
	print("Models loaded successfully!")


if __name__ == "__main__":
	print(("* Loading Keras model and Flask starting server..."
		"please wait until server has fully started"))
	load_models()
	app.run(host='0.0.0.0', threaded=False, debug=False)



# import requests, os, io, json, base64, pymongo, random
# from pathlib import Path
# from PIL import Image
# from bson import Binary
# import matplotlib.pyplot as plt


# client = pymongo.MongoClient(
# "mongodb+srv://user:fqg78pXPCpt8dtk@cluster0.xzh33.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
# # db = client.test
# # Database Name 
# db = client["images"] 
#   # Collection Name 
# collection = db["filters"] 


# filename='/home/dmytro/Projects/eleks_practice/label/keras-multi-label/dataset/categories/black_shoes/2.jpg'

# # inputTags = dict()
# # filename = os.fsdecode(filename)
# # url = 'http://0.0.0.0:5000/predict'
# # files = {'image': open(filename, 'rb')}
# # r = requests.post(url, files=files)
# # inputTags = r.json()
# # print('inputTags[filename]', inputTags)
# # print('inputTags[Item]', inputTags['item'])

# headers = {
#     "DbName": "images",
#     "CollName": "filters",
# }
# payload = {
#     "item": 'shoes',
#     "tags": ['shoes', 'black', 'sporty', 'woman', 'man', 'casual']
# }


# url_rec = 'http://0.0.0.0:5000/recommend'
# files = {'image': open(filename, 'rb')}
# rec = requests.post(url_rec, headers=headers, json=payload)
# getData = rec
# print("getData", getData)

# # print(inputTags)

# #coats  >=  33
# #pants  >=  50
# #skirts  >=  50
# #t-shirts  >=  70
# #sweaters  >=  50

# def get_all_tags():
#     itemTags = {}

#     analyzedImage = 'shoes'
    
#     look1 = {'shoes': 50, 'dresses': 50, 'coats': 50, 'pants': 50, 'shorts': 70, 'sweaters': 50, 't-shirts': 70, 'bags': 30 }

#     neededItems={}

#     for clothElement, similarity in look1.items():
#         neededItems[clothElement] = []
#         x = collection.find({'name': clothElement})
#         for data in x:
#             # print(data)
#             itemID = data['_id']
#             filterName = data['name']
#             imageName = data['imageName']
#             getImage = data['img']
#             getTags = data['tags']
#             for k,v in getData.items():
#                 res = format((len(set(v) & set(getTags)) / float(len(set(v) | set(getTags))) * 100), ".0f")
#                 # print("Similarity is = " + str(res) + ' | ' + str(getTags))
#                 if(int(res) >= similarity):
#                     neededItems[clothElement].append(itemID)
#                     itemTags[itemID] = getTags
#                     os.makedirs(filterName, exist_ok=True)
#                     with open(filterName + '/' + imageName, "wb") as f:
#                         f.write(base64.decodestring(getImage))
#     print(len(head))
#     if len(head) == 1:
#         create_looks_from_single_item(neededItems, analyzedImage)

# def create_looks_from_single_item(neededItems, analyzedImage):
#     shoes = {'look1': ["pants", "t-shirts"], 'look2': ["pants", "sweaters"], 'look3': ["shorts", "t-shirts"]}
#     dresses = {'look1': ["shoes", "bags"], 'look2': ["shoes", "bags"], 'look3': ["shoes", "coats"]}
#     coats = {'look1': ["shoes", "pants", "sweaters"], 'look2': ["shoes", "pants", "t-shirts"], 'look3': ["shoes", "pants", "sweaters"]}
#     pants = {'look1': ["shoes", "t-shirts"], 'look2': ["shoes", "sweaters"], 'look3': ["shoes", "sweaters", "coats"]}
#     shorts = {'look1': ["shoes", "t-shirts"], 'look2': ["shoes", "t-shirts"], 'look3': ["shoes", "t-shirts"]}
#     sweaters = {'look1': ["shoes", "pants"], 'look2': ["shoes", "pants"], 'look3': ["shoes", "pants", "coats"]}
#     t_shirts = {'look1': ["shoes", "pants"], 'look2': ["shoes", "pants"], 'look3': ["shoes", "shorts"]}
#     look = {}
    

#     if(analyzedImage=="shoes"):
#         generate_random_look(shoes, neededItems, look)
#     if(analyzedImage=="dresses"):
#         generate_random_look(dresses, neededItems, look)
#     if(analyzedImage=="coats"):
#         generate_random_look(coats, neededItems, look)
#     if(analyzedImage=="pants"):
#         generate_random_look(pants, neededItems, look)
#     if(analyzedImage=="shorts"):
#         generate_random_look(shorts, neededItems, look)
#     if(analyzedImage=="t_shirts"):
#         generate_random_look(t_shirts, neededItems, look)
#     if(analyzedImage=="sweaters"):
#         generate_random_look(sweaters, neededItems, look)
#     # if(analyzedImage=="skirts"):
#     #     generate_random_look(shoes, neededItems, look)

#     for k,v in look.items():
#         print(str(k) + ": " + str(v))


# def generate_random_look(item, neededItems, look):
#     for k,v in item.items():
#         look[k] = []
#         look[k].append('loadedImageID')
#         for s in v:
#             if(neededItems[s]==[]):
#                 look[k].append("Items doesn't fit!")
#             else:
#                 rand_choice = random.choice(neededItems[s])
#                 look[k].append(rand_choice)
                
#                 x = collection.find({'_id': rand_choice})
#                 for data in x:
#                     filterName = data['name']
#                     imageName = data['imageName']
#                     getImage = data['img']
                    
#                     os.makedirs(k, exist_ok=True)
#                     with open(k + '/' + imageName, "wb") as f:
#                         f.write(base64.decodestring(getImage))


# if __name__ == "__main__":
# 	get_all_tags()
#     # create_looks()
