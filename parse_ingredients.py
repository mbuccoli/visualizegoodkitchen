import json
import os

import logging
from recipes import load_recipes
logger = logging.getLogger("RECIPES")
logger.setLevel(logging.DEBUG)
logging.basicConfig(format='RECIPES:%(levelname)s:%(message)s', level=logging.DEBUG)


class Recipe():
	keys=["id","title", "url", "calories", "people", "ingredients",\
"tags", "url_image"]		
	def __init__(self):		
		self.id=""
		self.title=""
		self.url=url
		self.calories=""
		self.people=""
		self.ingredients=[]
		
		self.tags=[]
		self.url_image=""
		
	
	def save(self, out_dir):
		obj={}
		for k in self.keys:
			obj[k]=self.__dict__[k]
		with open(os.path.join(out_dir, self.id)+".json",'w') as fp:
			json.dump(obj, fp)
	
	def load(self, fn=""):
		with open(fn,'r') as fp:
			obj=json.load(fp)
		for k in self.keys:
			self.__dict__[k]=obj[k]
	
	def __repr__(self):
		name=""
		for k in self.keys:
			name+="%s - %s\n"%(k,str(self.__dict__[k]))
		return name			
		
def only_with_ingredients(recipes):
	return [r for r in recipes if r.ingredients!=[]]


if __name__=='__main__':
	
	rl= load_recipes("stored_recipes")
	rl=only_with_ingredients(rl)