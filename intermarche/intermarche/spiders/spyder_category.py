import scrapy
import json
from ..items import CategoryItem

class SpiderCategory(scrapy.Spider):
	""" Récupération de la lsite des catégories d'un magasin """
	name = "spider_category"
	allowed_domains = ['https://drive.intermarche.com', 'drive.intermarche.com']
	
	def start_requests(self):
		urls = [
			'https://drive.intermarche.com/153-mitry-mory',
		]
		
		for url in urls:
			yield scrapy.Request(url=url, callback=self.parse)

	def parse(self, response):
		items = []
		
		for sel in response.xpath("//div[contains(@class,'nav_sous-menu_bloc')]/div/ul/li/a"):
			url = sel.xpath('@href').extract()[0]

			if 'voir-tout' in url: # Non consideré
				continue

			data = sel.xpath('@href').extract()[0].split('/')

			# 1 - Création de l'item enfant
			item = CategoryItem()
			
			item['id'] = ""
			item['magasin_id'] = data[1].split('-')[0]
			
			# Trouver le rayon parent
			rayon = data[3]
			for elt in response.xpath("//div[contains(@class,'js-click_deployer js-univers')]"):
				tag = elt.xpath("@universtag").extract_first().replace('_', '-')
				name = elt.xpath("p/text()").extract_first()
				if tag == data[3]:
					item['rayon'] = name
					break
			
			# Trouver le rayon enfant (sous-rayon)
			for elt in response.xpath("//div[contains(@class,'nav_sous-menu_bloc')]/div"):
				sous_rayon = elt.xpath("ul/li/a/@href").extract_first().split('/')[4]
				if sous_rayon == data[4]:
					item['sous_rayon'] = elt.xpath("span/text()").extract_first()
					break
			
			item['categorie'] = sel.xpath('text()').extract()[0]
			item['categorie_id'] = data[5].split('-')[0]
			item['categorie_url'] = self.allowed_domains[0] + '/' + url
			item['feuille'] = str(True)

			# 2 - Create item Parent (rayon principal)
			item_parent = CategoryItem()
			
			item_parent['id'] = ""
			item_parent['magasin_id'] = data[1].split('-')[0]
			item_parent['rayon'] = name
			item_parent['sous_rayon'] = ""
			item_parent['categorie'] = ""
			item_parent['categorie_id'] = ""
			item_parent['categorie_url'] = ""
			item_parent['feuille'] = str(False)

			# 3 - Create item Enfant (sour-rayon)
			item_enfant = CategoryItem()

			item_enfant['id'] = ""
			item_enfant['magasin_id'] = data[1].split('-')[0]
			item_enfant['rayon'] = name
			item_enfant['sous_rayon'] = item['sous_rayon']
			item_enfant['categorie'] = ""
			item_enfant['categorie_id'] = ""
			item_enfant['categorie_url'] = ""
			item_enfant['feuille'] = str(False)

			yield item_parent

			yield item_enfant

			yield item
