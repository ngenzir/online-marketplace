
import os
import shutil
from PIL import Image
import random
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.urls import reverse
from django.utils.text import slugify
from django.core.files import File




from sellers.models import SellerAccount



def download_image_location(instance, filename):
	return "%s/%s" %(instance.slug, filename)


class Product(models.Model):
	seller = models.ForeignKey(SellerAccount, on_delete=models.CASCADE)
	images = models.ImageField(blank=True, null=True, upload_to=download_image_location, storage=FileSystemStorage())
	name = models.CharField(max_length=30)
	description = models.TextField()
	price = models.DecimalField(max_digits=100, decimal_places=2, default=19.99, null=True,)
	sale_active = models.BooleanField(default=False)
	sale_price = models.DecimalField(max_digits=100, decimal_places=2, default=12.99, null=True, blank=True)
	slug = models.SlugField(blank=True, unique=True)
	
	def __unicode__(self):
		return self.name

	def get_absolute_url(self):
		view_name = "products:detail_slug"
		return reverse(view_name, kwargs={"slug":self.slug})

	def get_edit_url(self):
		view_name = "sellers:product_edit"
		return reverse(view_name, kwargs={"pk":self.id})

	def get_download(self):
		view_name = "products:download_slug"
		url = reverse(view_name, kwargs={"slug": self.slug})
		return url


	@property
	def get_price(self):
		if self.sale_price and self.sale_active:
			return self.price

	def get_html_price(self):
		price = self.get_price
		if price ==self.sale_price:
			return "<p><span>%s</span> <span style='color:red;text-decoration:line-through;'>%s</span></p>" %(self.sale_price, self.price)

		else:
			return "<p>%<p>" %(self.price)

	

def create_slug(instance, new_slug=None):
	slug = slugify(instance.title)
	if new_slug is not None:
		slug = new_slug
	qs = Product.objects.filter(slug=slug)
	exits = qs.exits()
	if exists:
		new_slug = "%s-%s" %(slug, qs.first().id)
		return create_slug(instance, new_slug=new_slug)
	return slug

def product_pre_save_receiver(sender, instance, *args, **kwargs):
	if not instance.slug:
		instance.slug = create_slug(instance)

pre_save.connect(product_pre_save_receiver, sender=Product)


def thumbanail_location(instance, filename):
	return "%s/%s" %(instance.product.slug, filename)

THUMB_CHOICES = (
	("hd", "HD"),
	("sd", "SD"),
	("micro", "Micro"),
	)


class Thumbnail(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	type = models.CharField(max_length=20, choices=THUMB_CHOICES, default='hd')
	height = models.CharField(max_length=20, null=True, blank=True)
	width = models.CharField(max_length=20, null=True, blank=True)
	media = models.ImageField(
		width_field="width",
		height_field="height",
		blank=True,
		null=True,
		upload_to=thumbanail_location)

	def __unicode__(self):
		return str(self.media.path)


def create_new_thumbnail (media_path, instance, owner_slug):
	filename = os.path.basename(media_path)
	thumb = Image.open(media_path)
	size = (max_length, max_width)
	thumb.thumbnail(size, Image.ANTIALIAS)
	temp_loc = "%s/%s/tmp" %(settings.MEDIA_ROOT, owner_slug)
	if not os.path.exists(temp_loc):
		os.makedirs(temp_loc)
	temp_file_path = os.path.join(temp_loc, filename)
	if os.path.exists(temp_file_path):
		temp_path = os.path.join(temp_loc, "%s" %(random.random()))
		os.temp_file_path = os.path.join(temp_path, filename)
	temp_image = open(temp_file_path, "w")
	thumb.save(temp_image)
	thumb_data =open(temp_file_path, "r")

	thumb_file = File(thumb_data)
	instance.media.save(filename, thumb_file)
	shutil.rmtree(temp_loc, ignore_errors=True)
	return True


def product_post_save_receiver(sender, instance, created, *args, **kwargs):
	if instance.media:
		hd, hd_created = Thumbnail.objects.get_or_create(product=instance, type='hd')
		sd, sd_created = Thumbnail.objects.get_or_create(product=instance, type='sd')
		micro, micro_created = Thumbnail.objects.get_or_create(product=instance, type='micro')

		hd_max = (500, 500)
		sd_max = (350, 350)
		micro_max = (150, 150)

		media_path = instance.media.path
		owner_slug = instance.slug
		if hd_created:
			created_new_thumb(media_path, hd, owner_slug, hd_max[0], hd_max[1])

		if sd_created:
			created_new_thumb(media_path, sd, owner_slug, sd_max[0], sd_max[1])

		if micro_created:
			created_new_thumb(media_path, micro, owner_slug, micro_max[0], micro_max[1])



post_save.connect(product_post_save_receiver, sender=Product)


class MyProducts(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	products = models.ManyToManyField(Product, blank=True)

	def __unicode__(self):
		return "%s" %(self.product.count())

	class Meta:
		verbose_name ="My product"
		verbose_name_plural = "My Products"

