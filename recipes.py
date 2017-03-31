from html.parser import HTMLParser
import urllib.request as req
import json
import os

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
		with req.urlopen(url) as fp: 
			self.html_code=fp.read().decode("utf8")
		self.feed(self.html_code)

class IndexParser(GenericParser):
	recipe_item_class="archive-item-link "
	base_url="http://www.thegoodkitchen.it"
	def __init__(self, verbose=False):		
		GenericParser.__init__(self)
		self.recipes_links=[]		
		self.titles=[]
		self.verbose=verbose

	def add_recipe(self, attrs):		
		if "class" not in attrs:
			return
		
		if attrs["class"]==self.recipe_item_class:
			a_href=attrs["href"]
			self.recipes_links.append(self.base_url+a_href)		
			if self.verbose:
				print(a_href)
		

	def handle_starttag(self, tag, attrs):
		if tag=="a":
			attrs=list_to_dict(attrs)
			self.add_recipe(attrs)
	def save_recipes(self, out_file):
		with open(out_file,'w') as fp:
			json.dump(self.recipes_links,fp)

class RecipeParser(GenericParser):
	tag_function={"div":[start_image,end_image]}
	checks={'image':False}
	def __init__(self, verbose=False):		
		GenericParser.__init__(self, verbose=[])		
		self.title=""
		self.calories=0
		self.people=0
		self.ingredients=[]
		self.url_image=""
		checks={'image':False}
	def handle_starttag(self, tag, attrs):
		if tag=="a":
			attrs=list_to_dict(attrs)
			self.add_recipe(attrs)	
	
def get_recipes():
	if not os.path.exists(out_file)
		IP=IndexParser(False)
		IP.analyze_url(index_url)
		IP.save_recipes(out_file)
		recipes_links=IP.recipes_links
	else:
		with open(out_file,'r') as fp:
			recipes_links=json.load(fp)
	return recipes_links

def build_recipes():	
	recipes_links=get_recipes()

if __name__=='__main__':
	build_recipes()
