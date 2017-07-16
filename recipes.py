from html.parser import HTMLParser
import urllib.request as req
from urllib.error import HTTPError
import json
import os
import time
import logging
logger = logging.getLogger("RECIPES")
logger.setLevel(logging.DEBUG)
logging.basicConfig(format='RECIPES:%(levelname)s:%(message)s', level=logging.DEBUG)
index_url="http://www.thegoodkitchen.it/index/"
out_file='recipes.json'

# TODO: add logging methods

def list_to_dict(attrs):
	attrs_d={}
	for a in attrs:
		attrs_d[a[0]]=a[1]
	return attrs_d

class GenericParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.html_code=''
		
	def analyze_url(self, url):
		logging.debug("opening %s"%url)
		with req.urlopen(url) as fp: 
			self.html_code=fp.read().decode("utf8")
		self.feed(self.html_code)

class IndexParser(GenericParser):
	recipe_item_class="archive-item-link "
	base_url="http://www.thegoodkitchen.it"
	def __init__(self):		
		GenericParser.__init__(self)
		self.recipes_links=[]		
		self.titles=[]
		

	def add_recipe(self, attrs):		
		if "class" not in attrs:
			return
		
		if attrs["class"]==self.recipe_item_class:
			a_href=attrs["href"]
			self.recipes_links.append(self.base_url+a_href)		
			logger.info(a_href)
		

	def handle_starttag(self, tag, attrs):
		if tag=="a":
			attrs=list_to_dict(attrs)
			self.add_recipe(attrs)
	def save_recipes(self, out_file):
		with open(out_file,'w') as fp:
			json.dump(self.recipes_links,fp)

class RecipeParser(GenericParser):
	div_tags="blog-item-tags"
	div_id="blog-wrapper"
	meta_title="og:title"
	meta_image="og:image"
	keys=["id","title", "url", "calories", "people", "ingredients",\
		   "tags", "url_image"]		
	def __init__(self, url=""):		
		GenericParser.__init__(self)
		self.id=""
		self.title=""
		self.url=url
		self.calories=""
		self.people=""
		self.ingredients=[]
		
		self.tags=[]
		self.url_image=""
		self.checks={'tags':False,"category":False, "ingr": False}
		self.tag_function={	"div":[self.start_div,self.end_div],
					#"img":self.check_img, 
					#"title":[self.start_title,self.end_title], 
					"a":[self.start_a,self.end_a],
					"meta":self.check_meta}
	def start_div(self,attrs):		
		if "class" in attrs and attrs["class"]==self.div_tags:
			self.checks["tags"]=True
		elif "class" in attrs and attrs["class"]==self.div_id:
			self.id=attrs["data-item-id"]
	def end_div(self):
		if self.checks["tags"]:
			self.checks["tags"]=False
		
		
	def start_a(self, attrs):
		if "class" in attrs and self.a_category_class in attrs["class"]:
			self.checks["category"]=True		
	def end_a(self):
		pass
		
	def check_meta(self, attrs):
		if "property" in attrs and attrs["property"]==self.meta_title:
			self.title=attrs["content"]
		if "property" in attrs and attrs["property"]==self.meta_image:
			self.url_image=attrs["content"]
			
	def handle_starttag(self, tag, attrs):
		if tag in self.tag_function:
			try:
				fun=self.tag_function[tag][0]
				fun(list_to_dict(attrs))
			except:
				return
	def handle_endtag(self, tag):
		if tag in self.tag_function:
			fun=self.tag_function[tag][1]
			fun()
	def handle_startendtag(self,tag, attrs):
		if tag in self.tag_function:
			fun=self.tag_function[tag]
			fun(list_to_dict(attrs))
	def handle_data(self, data):		
		if self.checks["category"]:
			self.categories.append(data)
			self.checks["category"]=False
		elif "persone" in data.lower():			
			self.people=data
		elif "calorie" in data.lower():
			self.calories=data
		elif "ingredienti" in data.lower():
			self.checks["ingr"]=True
		elif "preparazione" in data.lower() or "procedimento" in data.lower():
			self.checks["ingr"]=False
		elif "function" in data.lower():
			self.checks["ingr"]=False
		elif self.checks["ingr"]:
			self.ingredients.append(data.lower())
		elif self.checks["tags"]:
			self.tags.append(data.lower())			
	def analyze_url(self):
		logger.info("Analysing %s"%self.url)
		try:			
			GenericParser.analyze_url(self, self.url)
		except HTTPError as HE:
			if "too many request" in str(HE):
				time.sleep(3)
				self.analyze_url()
		
	def __clean(self,what):
		new_items=[]
		for i in self.__dict__[what]:
			while '\n' in i:
				i=i.replace('\n','')
			while '  ' in i:
				i=i.replace('  ',' ')
			while ',' in i:
				i=i.replace(',','')	
			if i=='' or i==' ':
				continue
			if i.startswith(' '):
				i=i[1:]
			if i.endswith(' '):
				i=i[:-1]
			new_items.append(i)				
		self.__dict__[what]=new_items
	def clean_ingredients(self):
		self.__clean("ingredients")
	def clean_tags(self):
		self.__clean("tags")
		
	def clean(self):
		self.clean_ingredients()
		self.clean_tags()
	
	def save(self, out_dir):
		obj={}
		for k in self.keys:
			obj[k]=self.__dict__[k]
		with open(os.path.join(out_dir, self.id)+".json",'w') as fp:
			json.dump(obj, fp)
	
	def load(self, fn=""):
		with open(fn,'r') as fp:
			obj=json.load(fp)
		for k in self.keys():
			self.__dict__[k]=obj[k]
	
	def __repr__(self):
		name=""
		for k in self.keys:
			name+="%s - %s\n"%(k,str(self.__dict__[k]))
		return name			
		
def get_recipes(recompute):
	if not os.path.exists(out_file) or recompute:
		IP=IndexParser()
		IP.analyze_url(index_url)
		IP.save_recipes(out_file)
		recipes_links=IP.recipes_links
	else:
		with open(out_file,'r') as fp:
			recipes_links=json.load(fp)
	return recipes_links

def get_recipe(url):
	RP=RecipeParser(url)
	RP.analyze_url()
	RP.clean()
	return RP

def build_recipes(recompute=False):	
	recipes_links=get_recipes(recompute)
	recipes=list(map(get_recipe, recipes_links))
	
	return recipes
	
def save_recipes(recipes, dir_out):
	for r in recipes:
		r.save(dir_out)
	
if __name__=='__main__':
	rl= build_recipes(False)
	save_recipes(rl, 'recipes')
